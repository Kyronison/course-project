import pandas as pd
from app.services.tinkoff_api import get_figi_by_ticker, get_candles_data
from app.utils.utilities import quotation_to_float
import yfinance as yf
from app.models.models import HistoricalPrice, db
from sqlalchemy.dialects.postgresql import insert

BATCH_SIZE = 1000  # Установите размер пакета


def collect_stock_data(companies, days=365, use_db=True):
    """
        Собирает исторические данные о ценах акций и криптоактивов.

        Данные собираются либо с помощью yfinance (для тикеров, заканчивающихся на -USD),
        либо через Tinkoff API (для остальных тикеров). Собранные данные могут быть
        сохранены в базу данных или экспортированы в CSV файл.

        Args:
            companies (list): Список тикеров компаний/активов для сбора данных.
            days (int): Количество дней для сбора исторических данных (по умолчанию 365).
            use_db (bool): Если True, данные сохраняются в БД; если False, экспортируются в CSV.

        Returns:
            bool or pandas.DataFrame: Возвращает True/False в зависимости от успешности
                                      записи в БД (если use_db=True), либо pandas DataFrame
                                      (если use_db=False). Вызывает ValueError, если
                                      не удалось собрать данные при use_db=False.
    """
    all_data = {}
    new_records = []
    # Данные будут либо собираться для записи в БД, либо для формирования CSV.

    # Итерация по каждому тикеру для сбора данных
    for ticker in companies:
        try:
            # Обработка криптоактивов с помощью yfinance (используется для тикеров, заканчивающихся на -USD)
            if ticker.endswith("-USD"):
                crypto_data = yf.download(
                    ticker,
                    period=f"{days}d",
                    progress=False,
                    auto_adjust=True
                )
                if not crypto_data.empty:  # Проверка на пустой DataFrame
                    for date, row in crypto_data.iterrows():
                        date_str = date.strftime("%Y-%m-%d")
                        close_price = row["Close"]

                        if isinstance(close_price, pd.Series):
                            close_price = float(close_price.iloc[0])  # Извлекаем первое значение из Series

                        close_price = float(round(close_price, 4))  # Округляем после извлечения значения

                        if use_db:
                            new_records.append({
                                'ticker': ticker,
                                'date': date.date(),
                                'close': float(close_price)
                            })
                        else:
                            if date_str not in all_data:
                                all_data[date_str] = {}
                            all_data[date_str][ticker] = float(close_price)
                    print(f"Успешно: {ticker} (crypto)")
                else:
                    print(f"Нет данных для {ticker} (crypto)")
                    continue
            else:
                figi = get_figi_by_ticker(ticker)
                if not figi:
                    print(f"Тикер {ticker} не найден")
                    continue  # Пропускаем тикер, если FIGI не найден

                candles = get_candles_data(figi, days=days)
                if not candles:
                    print(f"Нет данных для {ticker}")
                    continue  # Пропускаем тикер, если нет данных свечей

                for candle in candles:
                    date = candle.time.date()
                    price = quotation_to_float(candle.close)

                    if use_db:
                        new_records.append({
                            'ticker': ticker,
                            'date': date,
                            'close': price
                        })
                    else:
                        date_str = candle.time.strftime("%Y-%m-%d")
                        if date_str not in all_data:
                            all_data[date_str] = {}
                        all_data[date_str][ticker] = price

                print(f"Успешно: {ticker} -> {figi}")

        except Exception as e:
            print(f"Ошибка для {ticker}: {str(e)}")
            continue

    # Блок записи собранных данных в базу данных (если use_db=True)
    if use_db:
        try:
            # Пакетная запись данных для оптимизации производительности
            for i in range(0, len(new_records), BATCH_SIZE):
                batch = new_records[i:i + BATCH_SIZE]
                stmt = insert(HistoricalPrice.__table__).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['ticker', 'date'],  # Указываем уникальный индекс
                    set_={'close': stmt.excluded.close}  # Обновляем цену
                )
                try:
                    db.session.execute(stmt)
                    db.session.commit()  # Сохраняем изменения после каждого пакета
                except Exception as e:
                    db.session.rollback()  # Откатываем изменения при ошибке
                    print(f"Ошибка при обработке пакета {i + 1} из {len(new_records) // BATCH_SIZE + 1}: {e}")
                    continue  # Пропускаем пакет с ошибкой
            print(f"Обновлено/добавлено записей в БД")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка записи в БД: {e}")
            return False
    else:
        if all_data:
            df = pd.DataFrame.from_dict(all_data, orient='index')
            df = df.sort_index().ffill()
            df.to_csv('stock_prices.csv', index_label='date')
            print("Данные сохранены в stock_prices.csv")
            return df
        else:
            raise ValueError("Не удалось собрать данные")

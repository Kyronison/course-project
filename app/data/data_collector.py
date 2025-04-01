import pandas as pd
from app.services.tinkoff_api import get_figi_by_ticker, get_candles_data
from app.utils.utilities import quotation_to_float
import yfinance as yf
from app.models.models import HistoricalPrice, db
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

BATCH_SIZE = 1000  # Установите размер пакета

def collect_stock_data(companies, days=365, use_db=True):
    all_data = {}
    new_records = []

    for ticker in companies:
        try:
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
                    continue

                candles = get_candles_data(figi, days=days)
                if not candles:
                    print(f"Нет данных для {ticker}")
                    continue

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

    # В data_collector.py замените блок записи в БД:
    if use_db:
        try:
            # Разделяем на пакеты и выполняем запросы
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

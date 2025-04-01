# data_loader.py
import pandas as pd
from app.models.models import HistoricalPrice, db
from app.services.tinkoff_api import get_forecast_by_ticker
from app.services.crypto.crypto_predictor import predict_future
from app.services.crypto.crypto_api import get_last_price_crypto


def load_clean_data(use_db=True):
    """
    Загружает данные из БД или CSV в зависимости от параметра use_db
    """
    if use_db:
        try:
            # Получаем все записи из БД
            records = db.session.query(
                HistoricalPrice.date,
                HistoricalPrice.ticker,
                HistoricalPrice.close
            ).all()

            # Создаем DataFrame напрямую из записей
            df = pd.DataFrame(
                records,
                columns=['date', 'ticker', 'close']
            )

            # Преобразуем в широкий формат
            df = df.pivot_table(
                index='date',
                columns='ticker',
                values='close',
                aggfunc='first'
            ).ffill().dropna(axis=1, how='all').dropna()
            print("DFNIK", df)
            return df

        except Exception as e:
            print(f"Ошибка загрузки данных из БД: {str(e)}")
            return pd.DataFrame()

    else:
        # Загружаем данные из CSV
        return pd.read_csv("stock_prices.csv",
                           index_col='date',
                           parse_dates=True) \
            .apply(pd.to_numeric, errors='coerce') \
            .dropna(axis=1, how='all') \
            .dropna()



def load_analyst_returns(companies, use_db=True):
    """
    Загружает или рассчитывает прогнозные доходности аналитиков.
    Функция возвращает словарь или Series с аналитическими данными.
    """
    mu_anal = {}

    for ticker in companies:
        if "-USD" not in ticker:  # Пропускаем криптовалюты
            forecast_data = get_forecast_by_ticker(ticker)
            print(forecast_data)
            # Проверяем, есть ли данные и содержит ли словарь ключ "price_change_rel"
            if forecast_data and isinstance(forecast_data, dict) and "price_change_rel" in forecast_data:
                price_change = forecast_data["price_change_rel"]
                mu_anal[ticker] = round(price_change / 100, 3)  # Конвертируем проценты в доли
            else:
                mu_anal[ticker] = 0  # Значение по умолчанию при отсутствии данных
        else:
            # Обработка криптовалют
            try:
                # Получаем текущую цену криптовалюты (из БД или crypto_api)
                if use_db:
                    last_record = HistoricalPrice.query.filter_by(ticker=ticker) \
                        .order_by(HistoricalPrice.timestamp.desc()).first()
                    if last_record:
                        current_price = last_record.price
                    else:
                        current_price = None
                else:
                    from app.services.crypto.crypto_api import get_last_price_crypto
                    current_price = get_last_price_crypto(ticker)

                if current_price is None:
                    print(f"Нет текущей цены для {ticker}, устанавливаем доходность 0")
                    mu_anal[ticker] = 0
                    continue

                # Формируем путь к модели без суффикса '_usd'
                model_path = "btc_model.h5"
                dates, preds = predict_future(model_path, ticker) #Тут поменял местами
                # Прогнозируемая цена на последнюю дату
                predicted_price = preds[-1]

                # Рассчитываем процент изменения
                price_change = (predicted_price - current_price) / current_price
                mu_anal[ticker] = float(round(price_change, 3))  # Возвращаем в виде десятичной дроби
            except Exception as e:
                print(f"Ошибка при прогнозировании для {ticker}: {e}")
                mu_anal[ticker] = 0  # Значение по умолчанию при ошибке

    return mu_anal

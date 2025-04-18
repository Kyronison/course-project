import yfinance as yf
from app.models.models import SectorData
import pandas as pd


def get_last_price_crypto(ticker: str) -> float:
    """
    Получает последнюю цену закрытия для указанного тикера с Yahoo Finance (через библиотеку yfinance).

    Args:
        ticker (str): Тикер актива (например: 'BTC-USD').

    Returns:
        float: Последняя доступная цена закрытия, округленная до двух знаков после запятой.
        None: Если данные для указанного тикера недоступны или произошла ошибка.
    """
    try:
        # Создаем объект Ticker
        asset = yf.Ticker(ticker)

        # Получаем данные за последний доступный торговый день
        history = asset.history(period="1d")

        # Если нет данных
        if history.empty:
            print(f"Нет данных для тикера {ticker}")
            return None

        # Возвращаем последнюю цену закрытия
        return round(history['Close'].iloc[-1], 2)

    except Exception as e:
        print(f"Ошибка при получении данных для {ticker}: {str(e)}")
        return None


def get_crypto_data(ticker, use_db=True):
    """
    Получает последнюю "цену" (или соответствующее значение) для криптовалюты
    из внутренней базы данных (SectorData) или из локального CSV файла,
    в зависимости от флага use_db.

    Note: Эта функция использует внутренние источники, отличные от get_last_price_crypto.

    Args:
        ticker (str): Тикер криптовалюты.
        use_db (bool): Если True, данные берутся из БД; если False, из CSV. По умолчанию True.

    Returns:
        float or None: Последняя доступная цена из выбранного источника или None,
                       если данные не найдены или произошла ошибка.
    """
    if use_db:
        last_record = SectorData.query.filter_by(ticker=ticker) \
            .order_by(SectorData.timestamp.desc()).first()
        return last_record.price if last_record else None
    else:
        # Старая реализация через CSV
        df = pd.read_csv("stock_prices.csv", index_col='date')
        return df[ticker].iloc[-1] if ticker in df.columns else None

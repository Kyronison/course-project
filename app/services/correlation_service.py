import pandas as pd
from app.services.tinkoff_api import create_sector_index, fetch_ticker_data
from app.utils.data_processing import normalize_data, align_series, process_timezones


def get_correlation_data(sector_tickers, crypto_ticker):
    # Получаем данные
    sector_series = create_sector_index(sector_tickers)
    crypto_series = fetch_ticker_data(crypto_ticker)

    # Обработка пустых данных
    if sector_series.empty or crypto_series.empty:
        return None

    # Нормализация криптовалюты
    crypto_series = normalize_data(crypto_series.to_frame()).iloc[:, 0]

    # Обработка временных зон
    sector_series, crypto_series = process_timezones(sector_series, crypto_series)

    # Совмещение данных
    aligned_df = align_series(sector_series, crypto_series)

    if aligned_df.empty:
        return None

    # Расчет корреляции
    correlation = aligned_df['sector'].corr(aligned_df['crypto'])
    return {
        'df': aligned_df,
        'correlation': 0.0 if pd.isna(correlation) else correlation
    }
import pandas as pd

def normalize_data(df):
    """Нормализация данных к начальному значению 100."""
    if df.empty:
        return df
    return df.div(df.iloc[0]) * 100

def align_series(sector_series, crypto_series):
    """Совмещение двух временных рядов по общим датам."""
    aligned_df = pd.concat([sector_series, crypto_series], axis=1, join='inner')
    aligned_df.columns = ['sector', 'crypto']
    return aligned_df.dropna()

def process_timezones(*series_list):
    """Обработка временных зон и нормализация дат."""
    processed = []
    for series in series_list:
        s = series.copy()
        s.index = s.index.tz_convert('UTC').normalize()
        processed.append(s)
    return processed
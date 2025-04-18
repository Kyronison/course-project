import pandas as pd


def normalize_data(df):
    """
    Нормализует данные в каждой колонке DataFrame так, чтобы первое значение
    каждой колонки стало равным 100.

    Args:
        df (pandas.DataFrame): Входной DataFrame с данными.

    Returns:
        pandas.DataFrame: DataFrame с нормализованными данными. Возвращает исходный
                          DataFrame, если он пуст.
    """
    if df.empty:
        return df
    return df.div(df.iloc[0]) * 100


def align_series(sector_series, crypto_series):
    """
    Объединяет два временных ряда (Series) в один DataFrame, сохраняя только
    общие даты (индекс), присутствующие в обоих рядах.

    Args:
        sector_series (pandas.Series): Первый временной ряд (для сектора).
        crypto_series (pandas.Series): Второй временной ряд (для криптовалюты).

    Returns:
        pandas.DataFrame: DataFrame, содержащий две колонки ('sector', 'crypto')
                          с данными из исходных рядов, выровненными по общим датам.
                          Строки с любыми NaN также удаляются.
    """
    aligned_df = pd.concat([sector_series, crypto_series], axis=1, join='inner')
    aligned_df.columns = ['sector', 'crypto']
    return aligned_df.dropna()


def process_timezones(*series_list):
    """
    Обрабатывает временные зоны для одного или нескольких временных рядов.

    Преобразует индекс каждого ряда во временную зону UTC и затем нормализует
    его, оставляя только дату (без времени).

    Args:
        *series_list: Переменное количество временных рядов (pandas.Series)
                      для обработки.

    Returns:
        list: Список с обработанными временными рядами. Оригинальные ряды не изменяются.
    """
    processed = []
    for series in series_list:
        s = series.copy()
        s.index = s.index.tz_convert('UTC').normalize()
        processed.append(s)
    return processed

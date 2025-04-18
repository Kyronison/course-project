import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, BlackLittermanModel


def optimize_portfolio(df_clean, mu_anal, weights, max_asset_share):
    """
    Оптимизирует структуру портфеля (веса активов) с использованием модели Black-Litterman.

    Модель Black-Litterman объединяет исторические данные о доходности и риске
    с аналитическими прогнозами (представленными в mu_anal) для получения
    скорректированных ожидаемых доходностей. Далее используется Efficient Frontier
    для нахождения портфеля с максимальным коэффициентом Шарпа при заданных ограничениях.

    Args:
        df_clean (pandas.DataFrame): Очищенные исторические данные о ценах активов
                                     (индекс - дата, колонки - тикеры).
        mu_anal (dict or pandas.Series): Словарь или Series с аналитическими прогнозами
                                         доходности для активов (ключ/индекс - тикер, значение - прогноз доходности).
        weights (numpy.array): Начальные веса активов (не используются в текущей реализации функции).
        max_asset_share (float): Максимально допустимая доля одного актива в итоговом портфеле.

    Returns:
        OrderedDict: Словарь с оптимизированными весами активов (тикер: вес).
                     Возвращает пустой словарь ({}) в случае возникновения ошибки.
    """
    try:
        # Проверка входных данных
        if df_clean.empty:
            raise ValueError("df_clean пуст.")

        # Приводим mu_anal к pandas Series, если это словарь
        if isinstance(mu_anal, dict):
            mu_anal = pd.Series(mu_anal)

        if mu_anal.empty:
            raise ValueError("mu_anal пуст.")

        # Оставляем только общие тикеры (исправленная проверка)
        common_tickers = df_clean.columns.intersection(mu_anal.index)
        if common_tickers.empty:  # Используем .empty для Index
            raise ValueError("Нет общих тикеров между df_clean и mu_anal.")
        df_clean = df_clean[common_tickers]
        mu_anal = mu_anal[common_tickers]

        # Дополнительная проверка после фильтрации
        if df_clean.empty or mu_anal.empty:
            raise ValueError("Данные стали пустыми после фильтрации.")

        # Расчет доходностей и ковариации
        mu = expected_returns.mean_historical_return(df_clean)
        S = risk_models.sample_cov(df_clean.ffill().dropna())

        # Модель Black-Litterman
        bl = BlackLittermanModel(
            S,
            pi="equal",
            absolute_views=mu_anal.to_dict(),  # Используем словарь
            omega="default"
        )
        rets = bl.bl_returns()

        # Оптимизация
        ef = EfficientFrontier(rets, S, weight_bounds=(0, max_asset_share))
        ef.max_sharpe()
        optimized_weights = ef.clean_weights()

        return optimized_weights

    except Exception as e:
        print(f"Ошибка в optimize_portfolio: {str(e)}")
        return {}

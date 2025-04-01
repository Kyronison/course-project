import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, BlackLittermanModel


def optimize_portfolio(df_clean, mu_anal, weights, max_asset_share):
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

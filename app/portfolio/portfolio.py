# portfolio.py
import json
from app.portfolio.portfolio_optimization import optimize_portfolio
from app.data.data_loader import load_clean_data, load_analyst_returns
from app.data.market_data import update_sector_data, update_sector_data_in_db
from app.data.data_collector import collect_stock_data
from app.services.tinkoff_api import get_usd_rub_cbr
from app.portfolio.calculate_assets import calculate_purchases
from app.models.models import SectorData
import numpy as np
from app.services.crypto.crypto_api import get_last_price_crypto
from config.config import Config
from collections import OrderedDict
from sqlalchemy import and_


def extract_companies_and_weights(result):
    """
    Извлекает список компаний и их веса из результата формирования портфеля.
    Исключает компании с нулевым весом.
    """
    portfolio = result.get('portfolio', {})
    companies = []
    weights = []
    weight_dict = {}

    total_cost = sum(
        asset.get('total_cost', 0)
        for sector_data in portfolio.values()
        for asset in sector_data['assets']
    )

    if total_cost == 0:
        raise ValueError("Общая стоимость портфеля равна нулю. Проверьте данные.")

    for sector_data in portfolio.values():
        for asset in sector_data['assets']:
            if isinstance(asset, dict) and 'asset' in asset:
                asset_cost = asset.get('total_cost', 0)
                weight = asset_cost / total_cost

                # Добавляем только если вес больше нуля
                if weight > 0:
                    companies.append(asset['asset'])
                    weights.append(weight)
                    weight_dict[asset['asset']] = weight

    return companies, weights, weight_dict


def print_purchases_result(purchases_result):
    """
    Выводит детализированные результаты расчета покупок.

    Аргументы:
        purchases_result: Словарь с результатами расчета покупок.
    """
    print("\nДетализация покупок:")
    total_allocated = purchases_result.get('total_allocated', 0)
    remaining_budget = purchases_result.get('remaining_budget', 0)
    print(f"  Всего выделено: {total_allocated:.2f} руб.")
    print(f"  Остаток бюджета: {remaining_budget:.2f} руб.")

    for asset, details in purchases_result['purchases'].items():
        print(f"\n  Актив: {asset}")
        for key, value in details.items():
            print(f"    {key}: {value}")


def form_portfolio(sectors, selected_sectors, max_asset_share, total_budget, target_beta=1.0, include_crypto=False,
                   exchange_rate=75.0):
    """
    Формирует портфель для заданных секторов и, при необходимости, добавляет криптовалюту.
    Акции покупаются в рублях, криптовалюты — в долларах.

    Аргументы:
      - sectors: словарь со списками активов по секторам (включая Crypto)
      - selected_sectors: список секторов, выбранных пользователем
      - max_asset_share: максимальная доля бюджета для одной акции
      - total_budget: общий бюджет для инвестиций (в рублях)
      - target_beta: целевое значение beta (по умолчанию 1.0)
      - include_crypto: булев флаг, определяющий, нужно ли включать криптовалюты
      - exchange_rate: курс доллара к рублю (по умолчанию 75.0)

    Возвращает:
      Словарь с распределением бюджета по секторам и расчетом портфельной beta
    """
    portfolio = {}

    # Если крипта включена, добавляем сектор "Crypto" в список выбранных секторов
    if include_crypto and "Crypto" in Config.SECTORS:
        if "Crypto" not in selected_sectors:
            selected_sectors = selected_sectors + ["Crypto"]

    num_sectors = len(selected_sectors)
    budget_per_sector = total_budget / num_sectors if num_sectors > 0 else 0

    for sector in selected_sectors:
        if sector not in sectors:
            continue

        is_crypto_sector = (sector == "Crypto")
        assets = sorted(
            sectors[sector],
            key=lambda x: (
                abs(x.get('beta', 1.0) - target_beta),
                x.get('price', 0) * x.get('lot_size', 1)  # Для крипты lot_size=1
            )
        )

        allocations = []
        remaining_budget = budget_per_sector
        num_assets = len(assets)
        min_allocation = budget_per_sector / num_assets if num_assets > 0 else 0
        print(f"Для сектора {sector} min_allocation = {min_allocation}")

        for i, asset in enumerate(assets):
            price = float(asset.get('price', 1))
            lot_size = asset.get('lot_size', 1) if not is_crypto_sector else 1
            beta = asset.get('beta', 1.0)

            # Для крипты цена в долларах, для акций — в рублях
            if is_crypto_sector:
                price_rub = float(price) * exchange_rate  # Переводим цену в рубли для расчетов
            else:
                price_rub = price  # Цена уже в рублях

            allocation = {
                'asset': asset['name'],
                'beta': beta,
                'price': float(price_rub),  # Храним цену в рублях для единообразия
                'lot_size': lot_size,
                'quantity': 0,
                'total_cost': 0
            }
            allocations.append(allocation)

            unit_cost = allocation['price'] * allocation['lot_size']
            max_invest = min(
                budget_per_sector * max_asset_share,
                remaining_budget
            )

            if is_crypto_sector:
                # Для крипты покупаем на всю доступную сумму
                invest_amount = min(max_invest, remaining_budget)
                quantity = float(invest_amount / allocation['price'])
            else:
                # Для акций покупаем целыми лотами
                max_lots = int(max_invest // unit_cost)
                if max_lots == 0:
                    continue
                quantity = max_lots
                invest_amount = quantity * unit_cost

            if invest_amount > 0:
                allocation['quantity'] += quantity
                allocation['total_cost'] += invest_amount
                remaining_budget -= invest_amount
                print(f"Куплено {quantity} {allocation['asset']} на сумму {invest_amount}. Осталось {remaining_budget}")

            # Сохраняем результаты
            sector_data = {
                'assets': sorted(allocations, key=lambda x: x['beta']),
                'remaining_budget': remaining_budget,
                'sector_beta': sum(
                    a['beta'] * (a['total_cost'] / (budget_per_sector - remaining_budget))
                    for a in allocations if a['total_cost'] > 0
                ) if (budget_per_sector - remaining_budget) > 0 else 0
            }
            portfolio[sector] = sector_data

    # Расчет общей beta портфеля
    total_invested = sum(
        sum(a['total_cost'] for a in s['assets'])
        for s in portfolio.values()
    )

    portfolio_beta = sum(
        s['sector_beta'] * (sum(a['total_cost'] for a in s['assets']) / total_invested)
        for s in portfolio.values()
    ) if total_invested > 0 else 0

    return {'portfolio': portfolio, 'portfolio_beta': portfolio_beta}


def create_and_optimize_portfolio(
        selected_sectors: list,
        max_asset_share: float,
        total_budget: float,
        target_beta: float = 1.0,
        include_crypto: bool = True,
        use_db: bool = True  # Добавляем новый параметр
):
    """
    Формирует портфель, оптимизирует его и рассчитывает покупки на основе оптимизированных весов.

    Аргументы:
        selected_sectors: Список выбранных секторов
        max_asset_share: Максимальная доля бюджета для одного актива
        total_budget: Общий бюджет для инвестиций
        target_beta: Целевое значение beta (по умолчанию 1.0)
        include_crypto: Булев флаг для включения криптовалют (по умолчанию True)
        use_db: Использовать базу данных или CSV (по умолчанию True)

    Возвращает:
        Словарь с детализацией покупок
    """

    print("Начало create_and_optimize_portfolio")

    print("Получение курса обмена")
    exchange_rate = get_usd_rub_cbr()
    print(f"Курс обмена: {exchange_rate}")

    # Обновление данных по секторам
    # sectors_updated = update_sector_data()
    # print(f"Данные по секторам: {sectors_updated}")

    sectors_updated = {}
    sectors_to_process = selected_sectors.copy()
    if include_crypto and "Crypto" in Config.SECTORS:
        sectors_to_process.append("Crypto")

    for sector in sectors_to_process:
        if sector not in Config.SECTORS:
            continue
        # Получаем список тикеров для данного сектора из Config.SECTORS
        tickers_in_sector = [stock['name'] for stock in Config.SECTORS[sector]]

        if sector != "Crypto":
            # Запрашиваем из БД только те активы, которые принадлежат данному сектору
            stocks = SectorData.query.filter(SectorData.ticker.in_(tickers_in_sector)).all()
            updated_stocks = [
                {
                    "name": stock.ticker,
                    "price": stock.price,
                    "lot_size": stock.lot_size,
                    "beta": stock.beta
                }
                for stock in stocks
            ]
            sectors_updated[sector] = updated_stocks
        else:
            stocks = Config.SECTORS[sector]
            updated_stocks = [
                {
                    "name": stock['name'],
                    "price": get_last_price_crypto(stock['name']),
                    "beta": 1.0
                }
                for stock in stocks
            ]
            sectors_updated[sector] = updated_stocks
    print(f"Данные по секторам: {sectors_updated}")
    # Формирование портфеля
    result = form_portfolio(
        sectors_updated,
        selected_sectors,
        max_asset_share=max_asset_share,
        total_budget=total_budget,
        target_beta=target_beta,
        include_crypto=include_crypto,
        exchange_rate=exchange_rate
    )
    print(f"Результат формирования портфеля: {result}")

    print("Извлечение компаний и весов")
    companies, weights, weight_dict = extract_companies_and_weights(result)
    print(f"Компании: {companies}")
    print(f"Веса: {weights}")
    print(f"Словарь весов: {weight_dict}")

    print("Загрузка данных")
    collect_stock_data(companies, days=365, use_db=use_db)  # Передаем use_db
    print("Данные собраны в БД")
    df_clean = load_clean_data(use_db=use_db)  # Передаем use_db
    print("Данные загружены")
    mu_anal = load_analyst_returns(companies, use_db=use_db)  # Передаем use_db
    print(f"Очищенные данные: {df_clean}")
    print(f"Аналитические прогнозы: {mu_anal}")

    print("Преобразование весов в numpy array")
    weights_array = np.array(list(weight_dict.values()))
    print(f"Веса в виде numpy array: {weights_array}")

    print("Оптимизация портфеля")
    optimized_weights = optimize_portfolio(df_clean, mu_anal, weights_array, max_asset_share)
    print(f"Оптимизированные веса: {optimized_weights}")

    print("Расчет покупок")
    purchases_result = calculate_purchases(optimized_weights, total_budget, exchange_rate=exchange_rate)
    print_purchases_result(purchases_result)
    print(f"Результат расчета покупок: {purchases_result}")

    print("Конец create_and_optimize_portfolio")
    return purchases_result

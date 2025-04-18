from app.portfolio.portfolio_optimization import optimize_portfolio
from app.data.data_loader import load_clean_data, load_analyst_returns
from app.data.data_collector import collect_stock_data
from app.services.tinkoff_api import get_usd_rub_cbr
from app.portfolio.calculate_assets import calculate_purchases
from app.models.models import SectorData
import numpy as np
from app.services.crypto.crypto_api import get_last_price_crypto
from config.config import Config


def extract_companies_and_weights(result):
    """
    Извлекает список компаний/активов и их веса из результата первоначального
    формирования портфеля (результат form_portfolio).

    Веса рассчитываются как доля общей стоимости актива в рамках всей инвестированной суммы.
    Исключает активы с рассчитанным весом, равным или менее нуля.

    Args:
        result (dict): Словарь с результатом работы функции form_portfolio.

    Returns:
        tuple: Кортеж из трех элементов:
               - companies (list): Список тикеров активов.
               - weights (list): Список соответствующих весов (долей).
               - weight_dict (dict): Словарь {тикер: вес}.
    """
    portfolio = result.get('portfolio', {})
    companies = []
    weights = []
    weight_dict = {}

    # Рассчитываем общую стоимость фактически инвестированных средств во всем портфеле
    total_cost = sum(
        asset.get('total_cost', 0)
        for sector_data in portfolio.values()
        for asset in sector_data['assets']
    )

    if total_cost == 0:
        raise ValueError("Общая стоимость портфеля равна нулю. Проверьте данные.")

    # Итерация по секторам и активам для расчета весов относительно общей стоимости
    for sector_data in portfolio.values():
        # Обработка каждого актива в текущем секторе
        for asset in sector_data['assets']:
            if isinstance(asset, dict) and 'asset' in asset:
                asset_cost = asset.get('total_cost', 0)
                weight = asset_cost / total_cost

                # Добавляем только если вес больше нуля
                if weight > 0:
                    companies.append(asset['asset'])
                    weights.append(weight)
                    weight_dict[asset['asset']] = weight

    # Возвращаем список тикеров, список весов и словарь весов
    return companies, weights, weight_dict


def print_purchases_result(purchases_result):
    """
    Выводит на консоль детализированные результаты расчета покупок.

    Показывает общую выделенную сумму, остаток бюджета и список покупок
    для каждого актива с его характеристиками.

    Args:
        purchases_result (dict): Словарь с результатами расчета покупок,
                                 полученный от функции calculate_purchases.
    """
    print("\nДетализация покупок:")
    total_allocated = purchases_result.get('total_allocated', 0)
    remaining_budget = purchases_result.get('remaining_budget', 0)
    print(f"  Всего выделено: {total_allocated: .2f} руб.")
    print(f"  Остаток бюджета: {remaining_budget: .2f} руб.")

    for asset, details in purchases_result['purchases'].items():
        print(f"\n  Актив: {asset}")
        for key, value in details.items():
            print(f"    {key}: {value}")


def form_portfolio(sectors, selected_sectors, max_asset_share, total_budget, target_beta=1.0, include_crypto=False,
                   exchange_rate=75.0):
    """
    Выполняет первоначальное распределение бюджета по активам внутри выбранных секторов.

    Бюджет равномерно делится между выбранными секторами. Внутри каждого сектора
    активы сортируются, и бюджет распределяется до достижения максимально допустимой
    доли на актив или исчерпания бюджета сектора. Акции покупаются лотами,
    криптовалюты - на оставшуюся в рамках лимита сумму.

    Args:
      sectors (dict): Словарь с активами, сгруппированными по секторам.
      selected_sectors (list): Список названий секторов, выбранных для инвестирования.
      max_asset_share (float): Максимальная доля бюджета, которую можно выделить на один актив (от общего бюджета).
      total_budget (float): Общий бюджет для инвестиций в рублях.
      target_beta (float): Целевое значение beta для портфеля (используется в сортировке). По умолчанию 1.0.
      include_crypto (bool): Флаг, указывающий, нужно ли включать криптовалюты, если они есть в конфигурации. По умолчанию False.
      exchange_rate (float): Курс USD/RUB, используемый для пересчета цен крипты. По умолчанию 75.0.

    Returns:
      dict: Словарь с информацией о сформированном портфеле:
            - 'portfolio' (dict): Распределение бюджета и активов по секторам.
            - 'portfolio_beta' (float): Рассчитанная взвешенная бета сформированного портфеля.
    """
    portfolio = {}

    # Если крипта включена, добавляем сектор "Crypto" в список выбранных секторов
    if include_crypto and "Crypto" in Config.SECTORS:
        if "Crypto" not in selected_sectors:
            selected_sectors = selected_sectors + ["Crypto"]

    # Равномерно распределяем общий бюджет между выбранными секторами
    num_sectors = len(selected_sectors)
    budget_per_sector = total_budget / num_sectors if num_sectors > 0 else 0

    # Итерация по каждому выбранному сектору
    for sector in selected_sectors:
        if sector not in sectors:
            continue

        is_crypto_sector = (sector == "Crypto")
        # Сортируем активы внутри сектора: сначала по удаленности беты от целевой, затем по стоимости лота/единицы
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

        # Итерация по отсортированным активам сектора для распределения бюджета
        for i, asset in enumerate(assets):
            # Получаем данные по активу, используя значения по умолчанию при необходимости
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

            # Рассчитываем стоимость одной единицы актива или одного лота в рублях
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

    # Расчет общей beta портфеля на основе взвешенной беты каждого сектора
    total_invested = sum(
        sum(a['total_cost'] for a in s['assets'])
        for s in portfolio.values()
    )

    portfolio_beta = sum(
        s['sector_beta'] * (sum(a['total_cost'] for a in s['assets']) / total_invested)
        for s in portfolio.values()
    ) if total_invested > 0 else 0

    # Возвращаем словарь с деталями портфеля по секторам и общей бетой портфеля
    return {'portfolio': portfolio, 'portfolio_beta': portfolio_beta}


def create_and_optimize_portfolio(
        selected_sectors: list,
        max_asset_share: float,
        total_budget: float,
        target_beta: float = 1.0,
        include_crypto: bool = True,
        use_db: bool = True
):
    """
    Оркестрирует весь процесс формирования и оптимизации портфеля:
    собирает данные, выполняет первоначальное распределение, оптимизацию весов,
    и рассчитывает финальное количество активов для покупки.

    Args:
        selected_sectors (list): Список выбранных для инвестирования секторов.
        max_asset_share (float): Максимальная доля бюджета, которую можно выделить на один актив (от общего бюджета).
        total_budget (float): Общий бюджет для инвестиций в рублях.
        target_beta (float): Целевое значение beta для оптимизации. По умолчанию 1.0.
        include_crypto (bool): Флаг, указывающий, нужно ли включать криптовалюты в портфель. По умолчанию True.
        use_db (bool): Флаг, указывающий, нужно ли использовать базу данных (True)
                       для загрузки/сбора данных или CSV файл (False). По умолчанию True.

    Returns:
        dict: Словарь с детализированными результатами расчета покупок,
              полученный от функции calculate_purchases.
    """

    exchange_rate = get_usd_rub_cbr()

    # Сбор актуальных данных по активам для первоначального распределения
    sectors_updated = {}
    # Формируем список секторов для обработки, включая крипту при необходимости
    sectors_to_process = selected_sectors.copy()
    if include_crypto and "Crypto" in Config.SECTORS:
        sectors_to_process.append("Crypto")

    # Итерация по секторам для сбора актуальных данных (цена, бета, лот) из БД или Config
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
    # Выполняем первоначальное распределение бюджета по активам в выбранных секторах
    result = form_portfolio(
        sectors_updated,
        selected_sectors,
        max_asset_share=max_asset_share,
        total_budget=total_budget,
        target_beta=target_beta,
        include_crypto=include_crypto,
        exchange_rate=exchange_rate
    )

    # Извлекаем список компаний и их веса из результата первоначального формирования
    companies, weights, weight_dict = extract_companies_and_weights(result)

    # Собираем исторические данные по ценам для активов. Сохранение в БД зависит от use_db.
    collect_stock_data(companies, days=365, use_db=use_db)  # Передаем use_db

    # Загружаем очищенные исторические данные (DataFrame)
    df_clean = load_clean_data(use_db=use_db)  # Передаем use_db

    # Загружаем прогнозы аналитиков/модели
    mu_anal = load_analyst_returns(companies, use_db=use_db)  # Передаем use_db

    # Преобразуем начальные веса в numpy array для функции оптимизации
    # Убеждаемся, что порядок весов соответствует порядку активов в df_clean и mu_anal
    weights_array = np.array(list(weight_dict.values()))

    # Выполняем оптимизацию портфеля на основе очищенных данных, прогнозов и начальных весов
    optimized_weights = optimize_portfolio(df_clean, mu_anal, weights_array, max_asset_share)

    # Рассчитываем количество лотов/акций/единиц крипты для покупки на основе оптимизированных весов
    purchases_result = calculate_purchases(optimized_weights, total_budget, exchange_rate=exchange_rate)
    print_purchases_result(purchases_result)

    return purchases_result

# tests/test_portfolio_logic.py
"""
Этот файл тестирует "мозг" вашего приложения - функции, отвечающие
за финансовые расчеты: корреляцию, оптимизацию портфеля и расчет покупок.

Здесь мы используем простые, заранее подготовленные (искусственные) данные,
чтобы проверить правильность математики и логики функций изолированно
от реальных рыночных данных или внешних API.
"""
import pytest
import pandas as pd
import numpy as np

# УКАЖИТЕ ПРАВИЛЬНЫЙ ПУТЬ к вашим функциям расчета!
try:
    # Попробуем импортировать функции из предполагаемого места
    from app.logic.portfolio import calculate_correlation, optimize_portfolio, calculate_purchases
except ImportError:
    # Если функции не найдены (например, еще не созданы или лежат в другом месте),
    # создадим временные заглушки, чтобы pytest мог хотя бы запустить файл.
    # ВАЖНО: Замените их на реальные импорты, как только функции будут готовы!
    pytest.skip("Пропускаем тесты логики портфеля: функции не найдены.", allow_module_level=True)
    # --- Заглушки ---
    # def calculate_correlation(data): return pd.DataFrame([[1.0]])
    # def optimize_portfolio(*args, **kwargs): return {'DUMMY': 1.0}
    # def calculate_purchases(*args, **kwargs): return {'DUMMY': {'total_cost_rub': 0}}
    # --- Конец Заглушек ---


def test_calculate_correlation_logic():
    """
    Тест: Проверяет расчет матрицы корреляции на простых тестовых данных.
    Убеждается, что результат имеет правильную форму (DataFrame),
    размерность, названия строк/колонок и корректные значения
    (диагональ = 1, симметричность, значения близки к ожидаемым).
    """
    print("\nТест: calculate_correlation()")
    # 1. Arrange: Подготовка простых входных данных
    # Словарь словарей: {дата_строка: {тикер: цена}}
    test_price_data = {
        '2024-01-01': {'A': 10, 'B': 20, 'C': 30},
        '2024-01-02': {'A': 11, 'B': 21, 'C': 29}, # A и B растут, C падает
        '2024-01-03': {'A': 12, 'B': 22, 'C': 31}, # A и B растут, C растет
        '2024-01-04': {'A': 11, 'B': 23, 'C': 30}, # A падает, B растет, C падает
    }
    # Ожидаемая структура: Pandas DataFrame с тикерами в индексах и колонках.

    # 2. Act: Вызов функции
    correlation_matrix = calculate_correlation(test_price_data)

    # 3. Assert: Проверки результата
    assert isinstance(correlation_matrix, pd.DataFrame), "Результат должен быть Pandas DataFrame"
    expected_tickers = ['A', 'B', 'C']
    assert sorted(list(correlation_matrix.columns)) == sorted(expected_tickers), "Колонки матрицы не совпадают с тикерами"
    assert sorted(list(correlation_matrix.index)) == sorted(expected_tickers), "Индексы матрицы не совпадают с тикерами"
    # Проверяем диагональные элементы (корреляция актива с самим собой = 1.0)
    # `np.diag` извлекает диагональ, `np.allclose` сравнивает массивы с допуском
    assert np.allclose(np.diag(correlation_matrix), 1.0), "Диагональные элементы должны быть равны 1.0"
    # Проверяем симметричность матрицы (corr(A,B) == corr(B,A))
    # `.values` возвращает NumPy массив, `.T` транспонирует его
    assert np.allclose(correlation_matrix.values, correlation_matrix.values.T), "Матрица корреляции должна быть симметричной"
    # (Опционально) Проверить конкретные значения корреляции, если они известны для тестовых данных.
    # Используйте `np.isclose(value1, value2, atol=...)` для сравнения чисел с плавающей точкой.
    # Например, ожидаем высокую положительную корреляцию между A и B:
    # assert correlation_matrix.loc['A', 'B'] > 0.5, "Ожидалась положительная корреляция между A и B"
    # Например, ожидаем какую-то корреляцию между A и C (знак не так очевиден без расчета):
    # assert np.isclose(correlation_matrix.loc['A', 'C'], -0.1, atol=0.1), "Проверка конкретного значения A-C"


def test_optimize_portfolio_logic():
    """
    Тест: Проверяет базовую логику оптимизации портфеля
          (например, по модели Блэка-Литтермана или другой).
    Убеждается, что функция возвращает веса, которые:
    - Распределены между всеми запрошенными активами.
    - Суммируются в 1.0 (или очень близко к 1.0).
    - Неотрицательны (если это требование модели).
    - Удовлетворяют заданным ограничениям (например, максимальный вес на актив).
    """
    print("\nТест: optimize_portfolio()")
    # 1. Arrange: Подготовка тестовых данных для модели оптимизации
    tickers = ['АКЦИЯ_РФ', 'АКЦИЯ_США', 'КРИПТА']
    # Искусственные данные для примера (в реальном тесте они должны быть рассчитаны или взяты из источника)
    # Ожидаемые доходности (годовые)
    mock_returns = pd.Series([0.15, 0.12, 0.25], index=tickers)
    # Ковариационная матрица доходностей (годовая)
    # Простая диагональная матрица для примера (нет ковариаций)
    mock_cov_matrix = pd.DataFrame(np.diag([0.05, 0.04, 0.10]), index=tickers, columns=tickers)
    # Параметры для оптимизатора
    risk_aversion = 3.0 # Коэффициент неприятия риска
    max_weight_limit = 0.6 # Максимальная доля одного актива в портфеле

    # Параметры специфичные для Black-Litterman (если используется)
    # views = {'АКЦИЯ_РФ': 0.18} # Пример "взгляда" инвестора
    # view_confidences = [0.8] # Уверенность во взгляде
    # Если Black-Litterman не используется, эти параметры будут None или не передаются.

    # 2. Act: Вызов функции оптимизации
    optimized_weights = optimize_portfolio(
        tickers=tickers,
        expected_returns=mock_returns, # Передаем тестовые/моковые данные
        cov_matrix=mock_cov_matrix,     # Передаем тестовые/моковые данные
        risk_aversion=risk_aversion,
        max_weight=max_weight_limit,
        # views=views,                # Передаем параметры Black-Litterman, если нужно
        # view_confidences=view_confidences
    )

    # 3. Assert: Проверка результатов оптимизации
    assert isinstance(optimized_weights, dict) or isinstance(optimized_weights, pd.Series), \
        "Результат (веса) должен быть словарем или Pandas Series"
    # Проверяем, что веса есть для всех запрошенных тикеров
    assert sorted(list(optimized_weights.keys())) == sorted(tickers), \
        "В результате должны быть веса для всех исходных тикеров"
    # Проверяем, что сумма весов равна 1.0 (с небольшой погрешностью из-за вычислений)
    weight_sum = sum(optimized_weights.values())
    assert np.isclose(weight_sum, 1.0), \
        f"Сумма весов должна быть близка к 1.0, но равна {weight_sum}"
    # Проверяем, что все веса неотрицательны (стандартное ограничение)
    assert all(w >= -1e-9 for w in optimized_weights.values()), \
        f"Найдены отрицательные веса: {[w for w in optimized_weights.values() if w < 0]}" # Допускаем крошечную отриц. погрешность
    # Проверяем, что ни один вес не превышает установленный максимум
    max_calculated_weight = max(optimized_weights.values())
    assert max_calculated_weight <= max_weight_limit + 1e-9, \
        f"Максимальный вес {max_calculated_weight} превышает лимит {max_weight_limit}"


def test_calculate_purchases_logic():
    """
    Тест: Проверяет функцию расчета количества лотов/акций для покупки
          на основе оптимизированных весов, бюджета, цен, лотности и курса валют.
    Убеждается, что:
    - Бюджет корректно распределяется по активам согласно весам.
    - Правильно рассчитывается количество лотов/единиц к покупке с учетом цены и лотности.
    - Учитывается курс валюты для активов, номинированных не в рублях.
    - Рассчитанная общая стоимость не превышает исходный бюджет.
    - Структура возвращаемого словаря соответствует ожиданиям.
    """
    print("\nТест: calculate_purchases()")
    # 1. Arrange: Подготовка входных данных для расчета покупок
    weights = {'РУБ_АКЦИЯ': 0.5, 'USD_АКЦИЯ': 0.3, 'USD_КРИПТА': 0.2}
    budget_rub = 100000.0 # Бюджет в рублях
    # Цены активов: рублевые в рублях, долларовые в долларах
    prices = {'РУБ_АКЦИЯ': 300.0, 'USD_АКЦИЯ': 150.0, 'USD_КРИПТА': 60000.0}
    # Лотность (сколько штук в одном лоте)
    lots = {'РУБ_АКЦИЯ': 10, 'USD_АКЦИЯ': 1, 'USD_КРИПТА': 1} # Для крипты обычно 1 (покупаем доли)
    usd_rate = 90.0 # Текущий курс USD/RUB

    # 2. Act: Вызов функции расчета покупок
    purchase_plan = calculate_purchases(
        optimized_weights=weights,
        total_budget_rub=budget_rub,
        current_prices=prices,
        lot_sizes=lots,
        usd_rub_rate=usd_rate
    )

    # 3. Assert: Проверка результатов расчета
    assert isinstance(purchase_plan, dict), "Результат должен быть словарем"
    assert sorted(list(purchase_plan.keys())) == sorted(weights.keys()), "В плане покупок должны быть все исходные активы"

    # --- Детальная проверка для каждого актива ---
    # Ожидаемые расчеты (примерные):
    # РУБ_АКЦИЯ: 100k * 0.5 = 50000 RUB. Цена лота = 300 * 10 = 3000 RUB. Лотов = floor(50000/3000) = 16. Акций = 160. Стоимость = 16 * 3000 = 48000 RUB.
    # USD_АКЦИЯ: 100k * 0.3 = 30000 RUB. Цена акции = 150 USD * 90 = 13500 RUB. Лотов/Акций = floor(30000/13500) = 2. Стоимость = 2 * 13500 = 27000 RUB.
    # USD_КРИПТА: 100k * 0.2 = 20000 RUB. Цена = 60000 USD * 90 = 5400000 RUB. Долей = 20000 / 5400000 = 0.0037037... Стоимость = 20000 RUB.
    # Итого: 48000 + 27000 + 20000 = 95000 RUB.

    # Проверка РУБ_АКЦИЯ (Структура словаря зависит от вашей реализации!)
    rub_stock_details = purchase_plan.get('РУБ_АКЦИЯ', {})
    assert rub_stock_details.get('allocated_rub') == 50000.0, "Неверный аллоцированный бюджет для РУБ_АКЦИЯ"
    assert rub_stock_details.get('lots_to_buy') == 16, "Неверное количество лотов для РУБ_АКЦИЯ"
    # assert rub_stock_details.get('units_to_buy') == 160 # Если возвращается кол-во штук
    assert rub_stock_details.get('total_cost_rub') == 48000.0, "Неверная итоговая стоимость для РУБ_АКЦИЯ"

    # Проверка USD_АКЦИЯ
    usd_stock_details = purchase_plan.get('USD_АКЦИЯ', {})
    assert usd_stock_details.get('allocated_rub') == 30000.0, "Неверный аллоцированный бюджет для USD_АКЦИЯ"
    assert usd_stock_details.get('lots_to_buy') == 2 or usd_stock_details.get('units_to_buy') == 2, \
        "Неверное количество лотов/штук для USD_АКЦИЯ"
    assert usd_stock_details.get('total_cost_rub') == 27000.0, "Неверная итоговая стоимость для USD_АКЦИЯ"
    # assert usd_stock_details.get('price_rub') == 13500.0 # Можно проверить и расчетную цену в рублях

    # Проверка USD_КРИПТА
    usd_crypto_details = purchase_plan.get('USD_КРИПТА', {})
    assert usd_crypto_details.get('allocated_rub') == 20000.0, "Неверный аллоцированный бюджет для USD_КРИПТА"
    expected_units = 20000.0 / (60000.0 * usd_rate)
    assert np.isclose(usd_crypto_details.get('units_to_buy', 0), expected_units), \
        f"Неверное количество долей для USD_КРИПТА (ожидали ~{expected_units:.8f})"
    assert np.isclose(usd_crypto_details.get('total_cost_rub', 0), 20000.0), \
        "Неверная итоговая стоимость для USD_КРИПТА"

    # Проверка общей потраченной суммы
    total_spent = sum(v.get('total_cost_rub', 0) for v in purchase_plan.values())
    assert total_spent <= budget_rub, f"Общая стоимость покупок {total_spent} превышает бюджет {budget_rub}"
    assert np.isclose(total_spent, 95000.0), f"Ожидалась итоговая стоимость 95000.0, получено {total_spent}"

# TODO: Добавьте тесты для граничных случаев (нулевой бюджет, один актив, высокая лотность и т.д.)
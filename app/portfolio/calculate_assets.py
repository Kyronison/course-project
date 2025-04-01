from collections import OrderedDict
from app.services.tinkoff_api import get_figi_by_ticker, get_lot_by_ticker, get_last_price
from app.services.crypto.crypto_api import get_last_price_crypto
from app.services.crypto.crypto_predictor import predict_future


def calculate_purchases(
        optimized_weights: OrderedDict,
        total_budget: float,
        exchange_rate: float = 75.0
) -> dict:
    """
    Рассчитывает количество лотов/акций для покупки на основе оптимизированных весов.
    Автоматически определяет тип актива по имени (крипто содержит '-USD').

    Аргументы:
        optimized_weights: OrderedDict с весами активов
        total_budget: Общий бюджет в рублях
        exchange_rate: Курс USD/RUB

    Возвращает:
        Словарь с детализацией покупок
    """
    purchases = {}
    total_used = 0

    for asset, weight in optimized_weights.items():
        if weight <= 0:
            continue

        # Определяем тип актива
        is_crypto = '-USD' in asset

        allocation = {
            'target_weight': weight,
            'allocated_rub': weight * total_budget,
            'type': 'crypto' if is_crypto else 'stock'
        }

        if is_crypto:
            # Получаем прогнозируемую цену
            try:

                _, preds = predict_future(asset, f'models/trained_models/btc_model.h5')
                predicted_price = preds[-1]  # Последний прогнозируемый день
                print(preds)
                print("Predicted_price:", predicted_price)
            except Exception as e:
                print(f"Ошибка прогноза: {e}")
                predicted_price = get_last_price_crypto(asset)

            if not predicted_price:
                continue

            # Расчет в долларах по прогнозируемой цене
            cost_usd = (weight * total_budget) / exchange_rate
            quantity = cost_usd / get_last_price_crypto(asset)

            allocation.update({
                'quantity': float(quantity),
                'price_usd': float(predicted_price),
                'cost_usd': cost_usd,
                'cost_rub': cost_usd * exchange_rate,
                'forecast_price': float(predicted_price),
                'current_price': float(get_last_price_crypto(asset))  # Сохраняем текущую цену
            })
        else:
            # Расчет для акций
            figi = get_figi_by_ticker(asset)
            if not figi:
                continue
            price = get_last_price(figi)
            if not price:
                continue
            lot_size = get_lot_by_ticker(asset)
            if not lot_size:
                continue
            cost_per_lot = price * lot_size
            max_lots = int((weight * total_budget) // cost_per_lot)

            allocation.update({
                'lots': max_lots,
                'shares': max_lots * lot_size,
                'price_per_share': price,
                'cost_rub': max_lots * cost_per_lot
            })

        purchases[asset] = allocation
        total_used += allocation['cost_rub'] if 'cost_rub' in allocation else 0

    return {
        'purchases': purchases,
        'total_allocated': round(total_used, 2),
        'remaining_budget': round(total_budget - total_used, 2)
    }

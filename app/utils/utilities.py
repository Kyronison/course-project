# utilities.py

def quotation_to_float(quotation) -> float:
    """
    Преобразует объект Quotation из Tinkoff Invest API (с полями units и nano)
    в число с плавающей точкой.

    Args:
        quotation: Объект Quotation из Tinkoff Invest API. Ожидается наличие
                   атрибутов 'units' (целая часть) и 'nano' (дробная часть, 10^-9).

    Returns:
        float: Цена в виде числа с плавающей точкой, округленная до 4 знаков.
    """
    return round(quotation.units + quotation.nano / 1e9, 4)


def quotation_forecast_to_float(quotation) -> float:
    """
    Преобразует формат цены из словаря (с ключами "units" и "nano")
    в число с плавающей точкой.

    Этот формат используется в некоторых ответах API (например, для прогнозов).

    Args:
        quotation (dict): Словарь, ожидается наличие ключей "units" (int)
                          и "nano" (int, 10^-9).

    Returns:
        float: Цена в виде числа с плавающей точкой, округленная до 2 знаков.
    """
    units = int(quotation["units"])
    nano = int(quotation["nano"])
    return round(units + nano / 1e9, 2)


def extract_consensus_data(forecast_data: dict):
    """
    Извлекает структурированные данные консенсус-прогноза из общего словаря
    ответа API (например, от эндпоинта GetForecastBy).

    Использует функцию quotation_forecast_to_float для преобразования
    полей цены и изменения в формат float.

    Args:
        forecast_data (dict): Словарь с данными прогноза, полученный от API.
                              Ожидается наличие ключа "consensus", содержащего
                              подсловарь с данными прогноза аналитиков.

    Returns:
        dict or None: Словарь с извлеченными и преобразованными данными консенсус-прогноза
                      (current_price, consensus_price, price_change_rel)
                      в формате float, или None, если данные консенсус-прогноза не найдены.
    """
    if forecast_data and "consensus" in forecast_data:
        consensus = forecast_data["consensus"]
        current_price = quotation_forecast_to_float(consensus["currentPrice"])
        consensus_price = quotation_forecast_to_float(consensus["consensus"])
        price_change_rel = quotation_forecast_to_float(consensus["priceChangeRel"])
        return {
            "current_price": current_price,
            "consensus_price": consensus_price,
            "price_change_rel": price_change_rel
        }
    else:
        print("Консенсус-прогноз не найден в данных.")
        return None

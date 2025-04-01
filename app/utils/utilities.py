# utilities.py

def quotation_to_float(quotation) -> float:
    return round(quotation.units + quotation.nano / 1e9, 4)


def quotation_forecast_to_float(quotation) -> float:
    units = int(quotation["units"])
    nano = int(quotation["nano"])
    return round(units + nano / 1e9, 2)


def extract_consensus_data(forecast_data: dict):
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

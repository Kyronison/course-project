from flask import Blueprint, jsonify, request
from config.config import Config
from app.services.correlation_service import get_correlation_data

correlation_bp = Blueprint("correlation_bp", __name__)


@correlation_bp.route("/yfinance/compare", methods=["GET"])
def yfinance_compare():
    sector = request.args.get('sector')
    crypto = request.args.get('crypto')

    # Валидация параметров
    if sector not in Config.sectors_dict:
        return jsonify({"error": f"Неизвестный сектор: {sector}"}), 400
    if crypto not in Config.crypto_map:
        return jsonify({"error": f"Неизвестная криптовалюта: {crypto}"}), 400

    # Получение данных
    result = get_correlation_data(
        Config.sectors_dict[sector],
        Config.crypto_map[crypto]
    )

    if not result:
        return jsonify({"error": "Недостаточно данных для расчета"}), 500

    # Форматирование ответа
    dates = result['df'].index.strftime('%Y-%m-%d').tolist()
    return jsonify({
        'dates': dates,
        'sector_values': result['df']['sector'].round(2).tolist(),
        'crypto_values': result['df']['crypto'].round(2).tolist(),
        'correlation': round(result['correlation'], 4)
    })
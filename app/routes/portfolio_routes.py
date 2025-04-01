from flask import Blueprint, request, jsonify
from app.portfolio.portfolio import create_and_optimize_portfolio
from app.services.tinkoff_api import get_forecast_by_ticker
from app.services.crypto.crypto_predictor import predict_future
from app.services.crypto.crypto_api import get_last_price_crypto
import requests
from config.config import Config  # Импортируйте Config

portfolio_bp = Blueprint('portfolio', __name__)


def calculate_change(details):
    if not details.get('current_price') or not details.get('forecast_price'):
        return None
    change = ((details['forecast_price'] - details['current_price']) / details['current_price']) * 100
    return round(change, 2)


@portfolio_bp.route('/generate-portfolio', methods=['POST'])
def generate_portfolio():
    try:
        data = request.get_json()
        params = {
            'selected_sectors': data.get('sectors', []),
            'max_asset_share': data.get('max_share', 0.3),
            'total_budget': data.get('amount', 100000),
            'target_beta': data.get('risk_level', 1.0),
            'include_crypto': data.get('include_crypto', False)
        }
        print("params got")
        print(params)
        result = create_and_optimize_portfolio(**params)
        print("Vot on Result")
        print(result)
        # Добавление прогнозов
        forecasts = {}
        for asset, details in result['purchases'].items():
            # Модифицируем блок обработки криптовалюты
            if details['type'] == 'crypto':
                try:
                    replaced_name = asset.replace('-USD', '').lower()
                    current_price = float(get_last_price_crypto(asset))

                    # Если не удалось получить цену, используем резервное значение
                    if current_price is None:
                        current_price = details.get('price_usd', 0)  # Или другой источник

                    # Прогноз цены (оставьте вашу текущую логику)
                    _, preds = predict_future(asset, f'models/trained_models/{replaced_name}_model.h5')
                    last_pred = preds[-1]

                    print("last pred", last_pred)

                    # Передаем текущую и прогнозируемую цену
                    forecasts[asset] = {
                        'current_price': current_price,
                        'forecast_price': round(float(last_pred), 2),
                        'change_percent': round(float(((last_pred - current_price) / current_price) * 100), 2)
                    }
                    details['current_price'] = current_price  # Добавляем текущую цену в ответ
                except Exception as e:
                    print(f"Ошибка обработки криптовалюты: {str(e)}")
            else:
                forecast = get_forecast_by_ticker(asset)
                if forecast:
                    forecasts[asset] = {
                        'price': forecast.get('consensus_price', details['price_per_share']),
                        'change_percent': round(forecast.get('price_change_rel', 0), 2)
                    }
        print("forecasts got")
        formatted_purchases = []
        for asset, details in result['purchases'].items():
            #  Находим данные об активе в конфиге
            asset_data = None
            for sector_list in Config.SECTORS.values():
                for item in sector_list:
                    if item['name'] == asset:
                        asset_data = item
                        break
                if asset_data:
                    break

            item = {
                **details,
                'ticker': asset,
                'forecast_change': round(calculate_change(details), 2) if details['type'] == 'crypto' else None,
                'forecast': forecasts.get(asset, {}),
                'image_url': asset_data['image_url'] if asset_data else None,  # Добавляем URL изображения
                'company_name': asset_data['company_name'] if asset_data else 'N/A'  # Добавляем имя компании
            }
            formatted_purchases.append(item)

        print(formatted_purchases)

        return jsonify({
            'status': 'success',
            'total_allocated': result['total_allocated'],
            'remaining_budget': result['remaining_budget'],
            'purchases': formatted_purchases
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

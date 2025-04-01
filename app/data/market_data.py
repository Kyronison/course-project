# market_data.py
from config.config import Config
from app.services.tinkoff_api import get_last_price, get_uid_by_ticker, get_beta_by_ticker, get_lot_by_ticker
from app.services.crypto.crypto_api import get_crypto_data, get_last_price_crypto
from app.models.models import db, SectorData
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask import current_app


def update_sector_data():
    sectors_updated = {}
    for sector, stocks in Config.SECTORS.items():
        updated_stocks = []
        if sector != "Crypto":
            for stock in stocks:
                ticker = stock["name"]
                uid = get_uid_by_ticker(ticker)
                price = get_last_price(uid)
                beta = get_beta_by_ticker(ticker)
                lot = get_lot_by_ticker(ticker)
                updated_stock = {
                    "name": ticker,
                    "price": price,
                    "lot_size": lot,
                    "beta": beta
                }
                updated_stocks.append(updated_stock)
            sectors_updated[sector] = updated_stocks
        else:
            for stock in stocks:
                ticker = stock["name"]
                price = get_crypto_data(ticker)
                print(sector, price)
                beta = 1.0
                updated_stock = {
                    "name": ticker,
                    "price": price,
                    "beta": beta
                }
                updated_stocks.append(updated_stock)
            sectors_updated[sector] = updated_stocks
    return sectors_updated

def update_sector_data_in_db():
    with current_app.app_context():
        for sector, stocks in Config.SECTORS.items():
            updated_stocks = []
            for stock in stocks:
                ticker = stock["name"]
                price = None
                beta = None
                lot = None

                if sector != "Crypto":
                    uid = get_uid_by_ticker(ticker)
                    price = get_last_price(uid)
                    beta = get_beta_by_ticker(ticker) or 1.0
                    lot = get_lot_by_ticker(ticker)
                else:
                    price = get_last_price_crypto(ticker)
                    beta = 1.0
                    lot = 1

                if price is None:
                    print(f"Пропускаем {ticker}, так как цена отсутствует")
                    continue

                lot_size = float(lot) if lot is not None else 1.0

                updated_stock = {
                    "name": ticker,
                    "price": float(price),
                    "beta": float(beta),
                    "lot_size": lot_size
                }
                updated_stocks.append(updated_stock)

            # Обновляем данные в БД
            for stock in updated_stocks:
                existing = SectorData.query.filter_by(ticker=stock['name']).first()
                if existing:
                    existing.price = stock.get('price', 0.0)
                    existing.beta = stock.get('beta', 1.0)
                    existing.lot_size = stock.get('lot_size', 1.0)
                else:
                    new_stock = SectorData(
                        ticker=stock['name'],
                        price=stock.get('price', 0.0),
                        beta=stock.get('beta', 1.0),
                        lot_size=stock.get('lot_size', 1.0)
                    )
                    db.session.add(new_stock)
            db.session.commit()

        print("Данные по секторам обновлены в БД")
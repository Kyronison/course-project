from config.config import Config
from app.services.tinkoff_api import get_last_price, get_uid_by_ticker, get_beta_by_ticker, get_lot_by_ticker
from app.services.crypto.crypto_api import get_crypto_data, get_last_price_crypto
from app.models.models import db, SectorData
from flask import current_app


def update_sector_data():
    """
    Собирает текущие рыночные данные (цену, размер лота, бету) по активам,
    сгруппированным по секторам, согласно конфигурации.

    Использует Tinkoff API для обычных акций и отдельный API для криптовалют.

    Returns:
        dict: Словарь, где ключ - название сектора, значение - список словарей
              с актуальными данными по активам этого сектора.
    """
    sectors_updated = {}
    # Итерация по настроенным секторам и их активам
    for sector, stocks in Config.SECTORS.items():
        updated_stocks = []
        # Обработка обычных акций (не криптовалют) через Tinkoff API
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
        # Обработка криптовалют через крипто API
        else:
            for stock in stocks:
                ticker = stock["name"]
                price = get_crypto_data(ticker)
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
    """
    Собирает актуальные рыночные данные по активам из конфигурации
    и обновляет/создает соответствующие записи в таблице SectorData в базе данных.

    Использует Tinkoff API для акций и отдельный API для криптовалют.
    Данные обновляются посекторно, изменения сохраняются в БД после обработки каждого сектора.
    """
    # Обеспечиваем контекст Flask приложения для работы с расширениями, например, SQLAlchemy
    with current_app.app_context():
        # Итерация по настроенным секторам
        for sector, stocks in Config.SECTORS.items():
            updated_stocks = []
            # Обработка каждого актива в текущем секторе
            for stock in stocks:
                ticker = stock["name"]
                price = None
                beta = None
                lot = None

                # Получение данных для обычных акций через Tinkoff API
                if sector != "Crypto":
                    uid = get_uid_by_ticker(ticker)
                    price = get_last_price(uid)
                    beta = get_beta_by_ticker(ticker) or 1.0
                    lot = get_lot_by_ticker(ticker)
                else:
                    price = get_last_price_crypto(ticker)
                    beta = 1.0
                    lot = 1

                # Пропускаем актив, если не удалось получить его цену
                if price is None:
                    print(f"Пропускаем {ticker}, так как цена отсутствует")
                    continue

                # Преобразуем размер лота в float, устанавливая 1.0 по умолчанию, если лот не определен
                lot_size = float(lot) if lot is not None else 1.0

                updated_stock = {
                    "name": ticker,
                    "price": float(price),
                    "beta": float(beta),
                    "lot_size": lot_size
                }
                updated_stocks.append(updated_stock)

            # Обновление или создание записей для активов текущего сектора в таблице SectorData
            for stock in updated_stocks:
                existing = SectorData.query.filter_by(ticker=stock['name']).first()
                # Проверяем, существует ли запись для данного тикера в БД
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
            # Сохраняем изменения для текущего сектора в БД
            db.session.commit()

        print("Данные по секторам обновлены в БД")

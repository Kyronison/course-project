import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, date
from app.data.data_collector import collect_stock_data
from app.data.market_data import update_sector_data_in_db
from app.models.models import HistoricalPrice, SectorData
from sqlalchemy import insert
import logging

# Настройка логирования для тестов
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Фикстуры для моков
@pytest.fixture
def mock_successful_yf_download():
    """Мокает yfinance.download для успешной загрузки данных."""
    with patch('yfinance.download') as mock:
        mock.return_value = pd.DataFrame({'Close': [100.0]}, index=[datetime(2024, 1, 1)])
        yield mock

@pytest.fixture
def mock_tinkoff_api():
    """Мокает Tinkoff API для быстрого ответа."""
    with patch('app.services.tinkoff_api.get_figi_by_ticker') as mock_figi, \
         patch('app.services.tinkoff_api.get_candles_data') as mock_candles:
        mock_figi.return_value = 'BBG000B9XRY4'
        # Создаем Candle object, чтобы соответствовать структуре
        candle_mock = MagicMock(time=datetime(2024, 1, 1), close=MagicMock(units=250, nano=0))
        mock_candles.return_value = [candle_mock]
        yield mock_figi, mock_candles

@pytest.fixture
def mock_db_session():
    """Мокает сессию базы данных для изоляции тестов."""
    with patch('app.data.data_collector.db.session.add') as mock_add, \
         patch('app.data.data_collector.db.session.commit') as mock_commit:
        yield mock_add, mock_commit

# Тест для collect_stock_data
def test_collect_stock_data(mocker, init_database): # Убрал test_app, если он не нужен
    """Тест: Проверяет функцию collect_stock_data."""
    print("\nТест: collect_stock_data")

    # 1. Arrange: Настройка моков
    mock_yf_download = mocker.patch('yfinance.download')
    mock_get_figi = mocker.patch('app.services.tinkoff_api.get_figi_by_ticker')
    mock_get_candles = mocker.patch('app.services.tinkoff_api.get_candles_data')

    # Определяем возвращаемые значения моков
    mock_btc_data = pd.DataFrame({'Close': [50000.1]}, index=pd.DatetimeIndex(['2024-01-01']))
    mock_yf_download.return_value = mock_btc_data
    mock_get_figi.return_value = 'BBG000B9XRY4'
    candle_mock = MagicMock(time=datetime(2024, 1, 1), close=MagicMock(units=150, nano=500000000)) # 150.5
    mock_get_candles.return_value = [candle_mock]

    companies_to_test = ['BTC-USD', 'SBER']
    days_to_test = 1

    # 2. Act: Вызов функции
    collect_stock_data(companies=companies_to_test, days=days_to_test, use_db=True)

    # 3. Assert: Проверка
    mock_yf_download.assert_called_once()
    mock_get_figi.assert_called_once_with('SBER')
    mock_get_candles.assert_called_once()

    # Проверяем, что данные были добавлены в базу данных
    with init_database.app.app_context(): # Используем app_context фикстуры init_database
        historical_prices = HistoricalPrice.query.all()
        assert len(historical_prices) == 2  # Ожидаем две записи (BTC-USD и SBER)
        assert historical_prices[0].ticker == 'BTC-USD'
        assert historical_prices[1].ticker == 'SBER'
        print("Тест пройден успешно!")

# Тест для update_sector_data_in_db
def test_update_sector_data_in_db(init_database, test_app):
    """Тест: Проверяет функцию update_sector_data_in_db."""
    print("\nТест: update_sector_data_in_db")

    # 1. Act: Вызов функции в контексте приложения
    with test_app.app_context():
        update_sector_data_in_db()

        # 2. Assert: Проверка результатов
        # Проверяем, что данные добавлены или обновлены в базе данных
        sector_data = SectorData.query.all()
        assert len(sector_data) == 3

        # Дополнительные проверки значений (пример)
        yandex_data = SectorData.query.filter_by(ticker='YDEX').first()
        assert yandex_data.price == 4414.5
        assert yandex_data.beta == 0.8
        assert yandex_data.lot_size == 1.0
        print("Тест пройден успешно!")
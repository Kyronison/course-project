# tinkoff_api.py
import http.client
import json
from datetime import timedelta
from tinkoff.invest import Client, CandleInterval, InstrumentIdType
from tinkoff.invest.utils import now
from config.config import Config
import requests
from app.utils.utilities import extract_consensus_data  # импорт функции из utilities.py
from app.utils.data_processing import normalize_data
import time
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
import yfinance as yf
import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


def get_usd_rub_cbr() -> float:
    """
    Возвращает официальный курс USD/RUB от ЦБ РФ
    """
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = response.json()
        return data["Valute"]["USD"]["Value"]
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None


def fetch_ticker_data(ticker):
    """Загрузка истории Close по одному тикеру из YahooFinance."""
    try:
        today = datetime.date.today()
        year_ago = today - datetime.timedelta(days=365)
        df = yf.Ticker(ticker).history(start=year_ago, end=today)
        return df["Close"].rename(ticker) if not df.empty else pd.Series()
    except Exception:
        return pd.Series()


def create_sector_index(tickers):
    """Создание индекса для списка тикеров (средняя после нормализации)."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_ticker_data, tickers))

    sector_df = pd.concat(results, axis=1)
    sector_df.dropna(axis=1, how="all", inplace=True)

    if sector_df.empty:
        return pd.Series(dtype=float)

    sector_df.dropna(axis=0, how="all", inplace=True)
    return normalize_data(sector_df).mean(axis=1)

@lru_cache(maxsize=100)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_figi_by_ticker(ticker: str) -> str:
    time.sleep(0.5)
    if "-USD" in ticker:
        return None
    with Client(Config.TOKEN) as client:
        try:
            response = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                class_code="TQBR",
                id=ticker
            )
            if not response.instrument:
                raise ValueError()
            return response.instrument.figi
        except:
            raise ValueError(f"Инструмент {ticker} не найден")
@lru_cache(maxsize=100)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_beta_by_ticker(ticker: str) -> float:
    time.sleep(0.5)
    """Возвращает коэффициент beta для указанного тикера."""
    try:
        asset_uid = get_assetuid_by_ticker(ticker)
        if not asset_uid:
            return None

        conn = http.client.HTTPSConnection("invest-public-api.tinkoff.ru")
        payload = json.dumps({"assets": [asset_uid]})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {Config.TOKEN}'
        }

        conn.request("POST", "/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/GetAssetFundamentals",
                    payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))

        if data.get('fundamentals') and len(data['fundamentals']) > 0:
            return data['fundamentals'][0].get('beta')

        return None

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def get_uid_by_ticker(ticker: str) -> str:
    if "-USD" in ticker:
        return None
    with Client(Config.TOKEN) as client:
        try:
            response = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                class_code="TQBR",
                id=ticker
            )
            if not response.instrument:
                raise ValueError()
            return response.instrument.uid
        except:
            raise ValueError(f"Инструмент {ticker} не найден")

def get_lot_by_ticker(ticker: str) -> str:
    if "-USD" in ticker:
        return None
    with Client(Config.TOKEN) as client:
        try:
            response = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                class_code="TQBR",
                id=ticker
            )
            if not response.instrument:
                raise ValueError()
            return response.instrument.lot
        except:
            raise ValueError(f"Инструмент {ticker} не найден")

def get_candles_data(figi, days=365):
    if not figi:
        return []
    with Client(Config.TOKEN) as client:
        candles = client.market_data.get_candles(
            figi=figi,
            from_=now() - timedelta(days=days),
            to=now(),
            interval=CandleInterval.CANDLE_INTERVAL_DAY
        )
        return candles.candles if candles.candles else []

def get_assetuid_by_ticker(ticker: str) -> str:
    if "-USD" in ticker:
        return None
    try:
        with Client(Config.TOKEN) as client:
            response = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                class_code="TQBR",
                id=ticker
            )
            if response.instrument:
                return response.instrument.asset_uid
            return None
    except Exception as e:
        print(f"Ошибка при поиске инструмента: {e}")
        return None
@lru_cache(maxsize=100)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_forecast_by_ticker(ticker: str, is_sandbox: bool = True):
    time.sleep(0.5)
    if is_sandbox:
        conn = http.client.HTTPSConnection("sandbox-invest-public-api.tinkoff.ru")
    else:
        conn = http.client.HTTPSConnection("invest-public-api.tinkoff.ru")
    uid = get_uid_by_ticker(ticker)
    payload = json.dumps({"instrumentId": uid})
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {Config.TOKEN}'
    }
    try:
        conn.request("POST", "/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/GetForecastBy",
                     payload, headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        if json_data:
            consensus_data = extract_consensus_data(json_data)
            if consensus_data:
                return consensus_data
            else:
                print("Не удалось извлечь данные о консенсус-прогнозе.")
                return None
        else:
            print(f"Не удалось получить прогнозы для тикера {ticker}.")
            return None
    except Exception as e:
        print(f"Ошибка при запросе прогноза для тикера {ticker}: {e}")
        return None
@lru_cache(maxsize=100)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_last_price(instrument_id):
    time.sleep(0.5)
    import requests
    url = "https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices"
    headers = {
        "Authorization": f"Bearer {Config.TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"instrumentId": [instrument_id], "instrumentStatus": "INSTRUMENT_STATUS_ALL"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        last_prices = data.get('lastPrices', [])
        if not last_prices:
            print(f"No price data found for instrument {instrument_id}")
            return None
        for price_data in last_prices:
            if 'price' in price_data:
                price_info = price_data['price']
                try:
                    units = int(price_info['units'])
                    nano = int(price_info['nano'])
                    return units + nano / 1e9
                except (KeyError, ValueError):
                    continue
        print("Valid price data not found in response")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

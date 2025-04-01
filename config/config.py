import os
from dotenv import load_dotenv

load_dotenv()  # Если используете файл .env

class Config:
    # Пример: если не задали в переменных окружения, укажите напрямую
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASS = os.getenv("PG_PASS", "aviasales")
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", "5432")
    PG_DB = os.getenv("PG_DB", "my_db")
    ETHERSCAN_API_KEY = "2NP9UXQZZUWR7F31YKMMSTSMV21Y4GTU7I"
    INFURA_URL = "https://mainnet.infura.io/v3/78a2b495bd904e6c8b971ea5b0a87d6a"
    TOKEN = os.getenv("TOKEN", "TOKEN")
    SECTORS = {
    "IT": [
        {"name": "YDEX", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:YDEX.png", "company_name": "Yandex"},
        {"name": "VKCO", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:VKCO.png", "company_name": "VK"},
        {"name": "HEAD", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:HEAD.png", "company_name": "HeadHunter"},
        {"name": "POSI", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:POSI.png", "company_name": "Positive Technologies"},
        {"name": "ASTR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:ASTR.png", "company_name": "Астра"},
        {"name": "SOFL", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:SOFL.png", "company_name": "Софтлайн"},
        {"name": "QIWI", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:QIWI.png", "company_name": "Qiwi"},
        {"name": "DELI", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:DELI.png", "company_name": "Делимобиль"},
        {"name": "DATA", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:DATA.png", "company_name": "Аренадата"},
        {"name": "DIAS", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:DIAS.png", "company_name": "Диасофт"}
    ],
    "Raw": [
        {"name": "GMKN", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:GMKN.png", "company_name": "Норникель"},
        {"name": "MTLR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MTLR.png", "company_name": "Мечел"},
        {"name": "PLZL", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:PLZL.png", "company_name": "Полюс"},
        {"name": "RUAL", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:RUAL.png", "company_name": "Русал"},
        {"name": "MAGN", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MAGN.png", "company_name": "Магнитогорский МК"},
        {"name": "ALRS", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:ALRS.png", "company_name": "Алроса"},
        {"name": "NLMK", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:NLMK.png", "company_name": "НЛМК"},
        {"name": "CHMF", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:CHMF.png", "company_name": "Северсталь"},
        {"name": "SGZH", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:SGZH.png", "company_name": "Segezha Group"},
        {"name": "TRMK", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:TRMK.png", "company_name": "ТМК"},
    ],
    "Transport": [
        {"name": "WUSH", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:WUSH.png", "company_name": "ВУШ Холдинг"},
        {"name": "FLOT", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:FLOT.png", "company_name": "Совкомфлот"},
        {"name": "EUTR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:EUTR.png", "company_name": "ЕвроТранс"},
        {"name": "FESH", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:FESH.png", "company_name": "FESCO"},
        {"name": "NMTP", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:NMTP.png", "company_name": "НМТП"}
    ],
    "HealthCare": [
        {"name": "MDMG", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MDMG.png", "company_name": "Мать и дитя"},
        {"name": "OZPH", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:OZPH.png", "company_name": "Озон Фармацевтика"},
        {"name": "PRMD", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:PRMD.png", "company_name": "Фармамед"}
    ],
    "RealEstate": [
        {"name": "SMLT", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:SMLT.png", "company_name": "Самолет"},
        {"name": "PIKK", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:PIKK.png", "company_name": "ПИК"},
        {"name": "LSRG", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:LSRG.png", "company_name": "ЛСР"}
    ],
    "Basic": [
        {"name": "X5", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:X5.png", "company_name": "X5 Retail Group"},
        {"name": "AFLT", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:AFLT.png", "company_name": "Аэрофлот"},
        {"name": "MGNT", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MGNT.png", "company_name": "Магнит"},
        {"name": "OZON", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:OZON.png", "company_name": "Ozon"},
        {"name": "MVID", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MVID.png", "company_name": "М.Видео"},
        {"name": "BELU", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:BELU.png", "company_name": "Белуга Групп"},
        {"name": "RAGR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:RAGR.png", "company_name": "Русагро"}
    ],
    "Telecom": [
        {"name": "MTSS", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MTSS.png", "company_name": "МТС"},
        {"name": "RTKM", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:RTKM.png", "company_name": "Ростелеком"}
    ],
    "Finance": [
        {"name": "SBER", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:SBER.png", "company_name": "Сбербанк"},
        {"name": "T", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:T.png", "company_name": "Тинькофф"},
        {"name": "VTBR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:VTBR.png", "company_name": "ВТБ"},
        {"name": "MOEX", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MOEX.png", "company_name": "Московская Биржа"},
        {"name": "AFKS", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:AFKS.png", "company_name": "Система"}
    ],
    "ElectroEnergy": [
        {"name": "UPRO", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:UPRO.png", "company_name": "Юнипро"},
        {"name": "IRAO", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:IRAO.png", "company_name": "Интер РАО"},
        {"name": "HYDR", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:HYDR.png", "company_name": "РусГидро"},
        {"name": "FEES", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:FEES.png", "company_name": "ФСК ЕЭС"},
        {"name": "MSNG", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:MSNG.png", "company_name": "Мосэнерго"}
    ],
    "Energy": [
        {"name": "GAZP", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:GAZP.png", "company_name": "Газпром"},
        {"name": "LKOH", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:LKOH.png", "company_name": "Лукойл"},
        {"name": "NVTK", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:NVTK.png", "company_name": "Новатэк"},
        {"name": "ROSN", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:ROSN.png", "company_name": "Роснефть"},
        {"name": "RNFT", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:RNFT.png", "company_name": "Сургутнефтегаз"},
        {"name": "TATN", "image_url": "https://beststocks.ru/api/file/stock/logos/RU:TATN.png", "company_name": "Татнефть"},
    ],
    "Crypto": [
        {"name": "BTC-USD", "image_url": "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=040", "company_name": "Bitcoin"}
    ]
    }
    sectors_dict = {
        "Technology": [
            "AAPL", "MSFT", "NVDA", "GOOG", "GOOGL", "META", "AVGO", "TSM", "V",
            "TCEHY", "MA", "ORCL", "NFLX", "BABA", "SAP", "TMUS", "ASML", "CRM",
            "CSCO", "IBM"
        ],
        "Utilities": [
            "NEE", "SO", "IBDRY", "DUK", "GEV", "ENLAY", "CEG", "NGG", "AEP", "D",
            "ENGIY", "SRE", "EXC", "VST", "PEG", "XEL", "EONGY", "ED", "PCG", "ETR"
        ],
        "RealEstate": [
            "PLD", "AMT", "WELL", "EQIX", "SPG", "PSA", "DLR", "O", "CCI", "CBRE",
            "VICI", "EXR", "AVB", "VTR", "SUHJY", "BEKE", "EQR", "IRM", "MTSFY", "CRBJY"
        ],
        "Industrials": [
            "GE", "SIEGY", "RTX", "CAT", "SPGI", "UNP", "EADSY", "DE", "BA", "FI",
            "ETN", "SAFRY", "LMT", "ABBNY", "UPS", "WM", "RCRUY", "RYCEY", "MCO", "CTAS"
        ],
        "HealthCare": [
            "LLY", "UNH", "JNJ", "ABBV", "NVO", "RHHBY", "MRK", "AZN", "ABT",
            "NVS", "TMO", "ISRG", "AMGN", "DHR", "PFE", "SNY", "GILD", "BSX",
            "SYK", "ESLOY"
        ],
        "Finance": [
            "JPM", "IDCBY", "BAC", "ACGBY", "WFC", "CICHY", "BACHY", "HSBC", "MS",
            "AXP", "GS", "PGR", "PGR", "RY", "CIHKY", "MUFG", "CMWAY", "ALIZY",
            "BLK", "SCHW"
        ],
        "Raw": [
            "XOM", "CVX", "SHEL", "TTE", "COP", "CSUAY", "ENB", "BP", "PBR", "EPD",
            "WMB", "EOG", "EQNR", "ET", "KMI", "OKE", "SLB", "MPLX", "PSX", "LNG"
        ],
        "Consumers": [
            "GCHOY", "BRK-B", "WMT", "PG", "KO", "NSRGY", "PM", "LRLCY", "PEP",
            "UL", "HON", "BUD", "HTHIY", "MO", "BTI", "MDLZ", "MMM", "ITW", "CL"
        ],
        "Basic": [
            "BHP", "AIQUY", "RIO", "SHW", "SCCO", "ECL", "APD", "ZIJMY", "SHECY",
            "FCX", "NEM", "AEM", "BASFY", "GLNCY", "GVDNY", "SXYAY", "VALE",
            "CTVA", "PTCAY", "NGLOY"
        ],
        "Crypto": ["BTC-USD"]
    }

    # 2) Маппинг для криптовалют, которые выбираются в <select>
    crypto_map = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "BNB": "BNB-USD",
        "ADA": "ADA-USD"
    }
    # Эта строка подключения пойдёт напрямую в SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "my_flask_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "my_jwt_secret")

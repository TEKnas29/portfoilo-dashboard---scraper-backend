import os
from dotenv import load_dotenv

load_dotenv()
APP_ENV = os.getenv("APP_ENV", "dev")
TZ = os.getenv("TZ", "Asia/Kolkata")
DATA_DIR = os.getenv("DATA_DIR", "./data")
PARQUET_DIR = os.getenv("PARQUET_DIR", f"{DATA_DIR}/parquet")
RAW_DIR = os.getenv("RAW_DIR", f"{DATA_DIR}/raw")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", f"{DATA_DIR}/processed")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCRAPE_HASHTAGS = [
    h.strip()
    for h in os.getenv(
        "SCRAPE_HASHTAGS", "#nifty50,#sensex,#intraday,#banknifty"
    ).split(",")
]
SCRAPE_MIN_TWEETS = int(os.getenv("SCRAPE_MIN_TWEETS", "2000"))
SCRAPE_MAX_CONCURRENCY = int(os.getenv("SCRAPE_MAX_CONCURRENCY", "4"))
SCRAPE_BACKEND = os.getenv("SCRAPE_BACKEND", "playwright")
PLOT_MAX_POINTS = int(os.getenv("PLOT_MAX_POINTS", "800"))

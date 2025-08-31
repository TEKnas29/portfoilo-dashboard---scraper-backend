from pathlib import Path
from app.config import DATA_DIR, PARQUET_DIR, RAW_DIR, PROCESSED_DIR

for p in [DATA_DIR, PARQUET_DIR, RAW_DIR, PROCESSED_DIR]:
    Path(p).mkdir(parents=True, exist_ok=True)

DATA_PATH = Path(DATA_DIR)
PARQUET_PATH = Path(PARQUET_DIR)
RAW_PATH = Path(RAW_DIR)
PROCESSED_PATH = Path(PROCESSED_DIR)
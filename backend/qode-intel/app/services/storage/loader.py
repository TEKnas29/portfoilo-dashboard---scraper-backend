import polars as pl
from datetime import datetime
from app.services.storage.paths import PARQUET_PATH
from app.utils.logging import logger

def load_last_24h(since_utc: datetime, until_utc: datetime) -> pl.DataFrame:
    # Load only likely partitions
    dates = set([since_utc.date().isoformat(), until_utc.date().isoformat()])
    dfs = []
    for d in dates:
        path = PARQUET_PATH / f"date={d}" / "tweets.parquet"
        if path.exists():
            dfs.append(pl.read_parquet(path))
    if not dfs:
        return pl.DataFrame([])
    df = pl.concat(dfs, how="vertical_relaxed")
    # Filter exact window
    df = df.filter((pl.col("timestamp") >= pl.lit(since_utc)) & (pl.col("timestamp") <= pl.lit(until_utc)))
    return df
from typing import Iterable
import polars as pl
from app.services.storage.paths import PARQUET_PATH

def to_polars_rows(items: Iterable[dict]) -> pl.DataFrame:
    df = pl.DataFrame(list(items))
    if df.is_empty():
        return df
    # Ensure proper dtypes
    if df.get_column("timestamp").dtype != pl.Datetime(time_unit="us", time_zone="UTC"):
        df = df.with_columns(
            pl.col("timestamp").dt.replace_time_zone("UTC").alias("timestamp")
        )
    return df

def write_parquet_partitioned(df: pl.DataFrame, partition_col: str = "date") -> str:
    if df.is_empty():
        return ""
    df2 = df.with_columns(
        pl.col("timestamp").dt.convert_time_zone("UTC").dt.date().cast(pl.String).alias(partition_col)
    )
    out_dir = PARQUET_PATH
    df2.write_parquet(out_dir / "_latest_batch.parquet")  # quick reference
    # Partitioned write: one file per day partition to control memory
    for day, sub in df2.partition_by(partition_col, as_dict=True).items():
        day_str = day[0] if isinstance(day, tuple) else str(day)
        day_dir = out_dir / f"date={day_str}"
        day_dir.mkdir(parents=True, exist_ok=True)
        sub.drop(partition_col).write_parquet(day_dir / "tweets.parquet", compression="zstd")
    return str(out_dir)
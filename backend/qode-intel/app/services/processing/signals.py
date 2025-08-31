import polars as pl
from app.utils.logging import logger

BULL_WORDS = {
    "buy",
    "long",
    "up",
    "breakout",
    "bull",
    "bullish",
    "rally",
    "green",
    "uptrend",
    "nifty",
    "sensex",
    "banknifty",
    "ath",
    "bo",
    "reversal",
    "bounce",
}
BEAR_WORDS = {
    "sell",
    "short",
    "down",
    "breakdown",
    "bear",
    "bearish",
    "fall",
    "red",
    "downtrend",
    "dump",
    "resistance",
    "rejection",
    "crash",
}


def lexical_signal(text: str) -> float:
    t = text.lower()
    bull = sum(1 for w in BULL_WORDS if w in t)
    bear = sum(1 for w in BEAR_WORDS if w in t)
    score = bull - bear
    if bull + bear == 0:
        return 0.0
    return max(-1.0, min(1.0, score / (bull + bear)))


def engagement_weight(row) -> float:
    # 1 + log-scaled engagement
    like = row.get("like_count", 0) or 0
    rt = row.get("retweet_count", 0) or 0
    rp = row.get("reply_count", 0) or 0
    qt = row.get("quote_count", 0) or 0
    s = like + 2 * rt + 0.5 * rp + 1.5 * qt
    import math

    return 1.0 + math.log1p(s)


def compute_composite(df: pl.DataFrame) -> pl.DataFrame:
    logger.info("In compute composite")
    if df.is_empty():
        return df

    # Compute lexical signal & weight
    df2 = df.with_columns(
        [
            pl.col("content")
            .map_elements(lexical_signal, return_dtype=pl.Float64)
            .alias("lex_signal"),
            pl.struct(["like_count", "retweet_count", "reply_count", "quote_count"])
            .map_elements(engagement_weight, return_dtype=pl.Float64)
            .alias("weight"),
        ]
    )

    # Time bucket (15m default)
    df2 = df2.with_columns([pl.col("timestamp").dt.truncate("15m").alias("bucket")])

    # Weighted mean per bucket
    grp = df2.group_by("bucket").agg(
        [
            (pl.col("lex_signal") * pl.col("weight")).sum().alias("wsum"),
            pl.col("weight").sum().alias("w"),
            pl.len().alias("n"),
            pl.col("lex_signal").mean().alias("mean_unweighted"),
            pl.col("lex_signal").std(ddof=1).alias("std_unweighted"),
        ]
    )

    grp = (
        grp.with_columns(
            [
                (pl.col("wsum") / pl.col("w")).alias("signal"),
                # 95% CI using unweighted std as conservative estimate
                (1.96 * (pl.col("std_unweighted") / (pl.col("n") ** 0.5))).alias(
                    "ci95"
                ),
            ]
        )
        .drop(["wsum", "w"])
        .sort("bucket")
    )

    return grp

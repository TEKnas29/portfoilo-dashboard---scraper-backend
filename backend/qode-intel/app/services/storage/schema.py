import polars as pl

TWEET_SCHEMA = pl.Schema(
    {
        "id": pl.String,
        "username": pl.String,
        "timestamp": pl.Datetime(time_unit="us", time_zone="UTC"),
        "content": pl.String,
        "like_count": pl.Int64,
        "retweet_count": pl.Int64,
        "reply_count": pl.Int64,
        "quote_count": pl.Int64,
        "mentions": pl.List(pl.String),
        "hashtags": pl.List(pl.String),
        "lang": pl.Utf8,
    }
)

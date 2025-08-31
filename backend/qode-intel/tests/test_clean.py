from app.services.processing.clean import clean_tweets
from app.models.tweet import Tweet
from datetime import datetime, timezone


def test_clean_basic():
    t = Tweet(
        id="1",
        username="u",
        timestamp=datetime.now(timezone.utc),
        content="Buy $NIFTY50 now! https://x.com ",
    )
    out = clean_tweets([t])[0]
    assert "http" not in out.content

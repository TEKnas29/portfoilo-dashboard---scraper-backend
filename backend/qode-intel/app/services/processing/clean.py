from typing import Iterable, List
from app.models.tweet import Tweet
from app.utils.text import clean_text, extract_entities


def clean_tweets(tweets: Iterable[Tweet]) -> List[Tweet]:
    out: List[Tweet] = []
    for t in tweets:
        text = clean_text(t.content)
        mentions, hashtags = extract_entities(text)
        out.append(Tweet(**{**t.model_dump(), "content": text, "mentions": mentions, "hashtags": hashtags}))
    return out
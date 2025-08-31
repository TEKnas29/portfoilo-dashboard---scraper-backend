from typing import Iterable, List
from hashlib import blake2b
from app.models.tweet import Tweet


def dedupe_tweets(tweets: Iterable[Tweet]) -> List[Tweet]:
    seen_ids = set()
    seen_hashes = set()
    out: List[Tweet] = []
    for t in tweets:
        if t.id in seen_ids:
            continue
        key = f"{t.username}|{t.timestamp.isoformat()}|{t.content}".encode("utf-8", errors="ignore")
        h = blake2b(key, digest_size=12).hexdigest()
        if h in seen_hashes:
            continue
        seen_ids.add(t.id)
        seen_hashes.add(h)
        out.append(t)
    return out
import re
import unicodedata
from typing import List, Tuple

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"(?<= )@([A-Za-z0-9_]{1,15})")
HASHTAG_RE = re.compile(r"(?<= )#(\w+)")
WHITESPACE_RE = re.compile(r"\s+")

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def extract_entities(text: str) -> Tuple[List[str], List[str]]:
    mentions = list({m.lower() for m in MENTION_RE.findall(" " + text)})
    hashtags = list({h.lower() for h in HASHTAG_RE.findall(" " + text)})
    return mentions, hashtags

def clean_text(text: str) -> str:
    t = normalize_unicode(text)
    t = URL_RE.sub("", t)
    t = t.replace("\n", " ")
    t = WHITESPACE_RE.sub(" ", t).strip()
    return t

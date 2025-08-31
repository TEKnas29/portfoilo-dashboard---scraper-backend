from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Tweet(BaseModel):
    id: str
    username: str
    timestamp: datetime
    content: str
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    mentions: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    lang: Optional[str] = None

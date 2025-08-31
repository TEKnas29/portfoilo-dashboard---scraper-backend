from fastapi import APIRouter, Query
from app.utils.time import last_24h_window
from app.services.storage.loader import load_last_24h
from app.services.processing.vectorize import build_tfidf

router = APIRouter(prefix="/process", tags=["process"])

@router.post("/tfidf")
async def build_vectors(max_features: int = Query(20000, ge=500, le=50000)):
    since_utc, until_utc = last_24h_window()
    df = load_last_24h(since_utc, until_utc)
    vect, X = build_tfidf(df, max_features=max_features)
    # Return only light metadata
    return {
        "docs": int(df.height),
        "vocab_size": int(len(vect.vocabulary_)),
        "shape": list(X.shape),
        "sample_terms": list(sorted(list(vect.vocabulary_.keys()))[:10]),
    }
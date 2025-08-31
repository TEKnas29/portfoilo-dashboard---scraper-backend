import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf(df: pl.DataFrame, max_features: int = 5000):
    """
    Build TF-IDF vectors from a Polars dataframe with a 'content' column.
    Cleans empty rows and avoids empty-vocab errors.
    """
    if "content" not in df.columns:
        raise ValueError("❌ DataFrame must contain a 'content' column.")

    # Convert to string, strip whitespace, fill nulls
    texts = (
        df["content"]
        .map_elements(lambda x: str(x).strip() if x is not None else "", return_dtype=pl.Utf8)
    )

    # Filter out empty strings
    texts = texts.filter(texts != "")

    if texts.is_empty():
        raise ValueError("❌ No valid text found in dataframe for TF-IDF.")

    # Convert to Python list for sklearn
    text_list = texts.to_list()

    vect = TfidfVectorizer(
        max_features=max_features,
        stop_words=None,  # don’t strip stopwords aggressively
        token_pattern=r"(?u)\b\w+\b"  # keep unicode word chars
    )

    X = vect.fit_transform(text_list)

    return vect, X

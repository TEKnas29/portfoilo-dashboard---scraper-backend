import io
import pandas as pd
import polars as pl
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
from app.config import PLOT_MAX_POINTS


def downsample(df: pl.DataFrame, max_points: int) -> pl.DataFrame:
    if df.height <= max_points:
        return df
    stride = max(1, df.height // max_points)
    return df[::stride]


def plot_signal(df: pl.DataFrame) -> bytes:
    if df.is_empty():
        fig = plt.figure(figsize=(1, 1))
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    df2 = df.select(["bucket", "signal", "ci95"]).sort("bucket")
    df2 = downsample(df2, PLOT_MAX_POINTS)

    x = pd.to_datetime(df2.get_column("bucket").to_pandas())
    y = df2.get_column("signal").to_numpy()
    ci = df2.get_column("ci95").to_numpy()

    fig = plt.figure(figsize=(9, 4))
    ax = plt.gca()
    if len(x) < 2:
        ax.plot(x, y, label="Composite Signal", marker="o")
    else:
        ax.plot(x, y, label="Composite Signal")
        ax.fill_between(x, y - ci, y + ci, alpha=0.2, label="95% CI")
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal (-1..1)")
    ax.legend()
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()

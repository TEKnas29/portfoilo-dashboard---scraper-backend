from fastapi import APIRouter, Response
from app.utils.time import last_24h_window
from app.services.storage.loader import load_last_24h
from app.services.processing.signals import compute_composite
from app.services.processing.visualize import plot_signal

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.get("/signal")
async def signal_json():
    since_utc, until_utc = last_24h_window()
    df = load_last_24h(since_utc, until_utc)
    comp = compute_composite(df)
    return comp.to_dict(as_series=False)


@router.get("/signal.png")
async def signal_png():
    since_utc, until_utc = last_24h_window()
    df = load_last_24h(since_utc, until_utc)
    comp = compute_composite(df)
    png = plot_signal(comp)
    return Response(content=png, media_type="image/png")

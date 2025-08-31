from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_health, routes_scrape, routes_process, routes_analyze
import asyncio
import sys
import platform

if platform.system() == 'Windows':
    # Configure event loop policy for Windows
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Qode Market Intelligence", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_scrape.router)
app.include_router(routes_process.router)
app.include_router(routes_analyze.router)

@app.get("/")
async def root():
    return {"app": "qode-market-intel", "endpoints": ["/health", "/scrape/start", "/scrape/status/{id}", "/process/tfidf", "/analyze/signal", "/analyze/signal.png"]}
import uuid
from typing import Dict
from fastapi import APIRouter, BackgroundTasks, Query, Depends
from app.config import SCRAPE_HASHTAGS, SCRAPE_MIN_TWEETS
from app.utils.time import last_24h_window, utc_now
from app.utils.logging import logger
from app.services.processing.clean import clean_tweets
from app.services.processing.dedupe import dedupe_tweets
from app.services.storage.writer import to_polars_rows, write_parquet_partitioned
from app.services.storage.paths import RAW_PATH
from app.deps import get_backend
import json

router = APIRouter(prefix="/scrape", tags=["scrape"])

JOBS: Dict[str, Dict] = {}

async def _run_job(job_id: str, hashtags, limit, backend):
    JOBS[job_id]["status"] = "running"
    try:
        since_utc, until_utc = last_24h_window()
        logger.info(f"Window UTC: {since_utc} → {until_utc}")

        tweets = await backend.pw.scrape_async(hashtags, since_utc, until_utc, limit)

        # Save raw JSONL for auditing
        raw_file = RAW_PATH / f"raw_{job_id}.jsonl"
        
        with raw_file.open("w", encoding="utf-8") as f:
            for t in tweets:
                f.write(json.dumps(t.model_dump(), ensure_ascii=False, default=str) + "\n")

        # Clean + dedupe
        cleaned = clean_tweets(tweets)
        unique = dedupe_tweets(cleaned)
        
        df = to_polars_rows([u.model_dump() for u in unique])
        outdir = write_parquet_partitioned(df)

        JOBS[job_id].update({
            "status": "done",
            "raw_count": len(tweets),
            "unique_count": len(unique),
            "parquet_dir": outdir,
        })
    except Exception as e:
        logger.exception("scrape job failed")
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)

@router.post("/start")
async def start_scrape(
    background: BackgroundTasks,
    hashtags: str = Query(
        ",".join(SCRAPE_HASHTAGS),
        description="Comma-separated list of hashtags (include #)"
    ),
    limit: int = Query(SCRAPE_MIN_TWEETS, ge=100, le=20000),
    backend = Depends(get_backend),
):
    tag_list = [h.strip() for h in hashtags.split(",") if h.strip()]
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued", "created_at": utc_now().isoformat(), "hashtags": tag_list, "limit": limit}
    background.add_task(_run_job, job_id, tag_list, limit, backend)
    return {"job_id": job_id, "status": JOBS[job_id]["status"]}

@router.get("/status/{job_id}")
async def job_status(job_id: str):
    return JOBS.get(job_id, {"error": "not found"})
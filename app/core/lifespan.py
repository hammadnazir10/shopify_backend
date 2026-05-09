"""FastAPI lifespan handler — replaces deprecated `@app.on_event`."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging, get_logger
from app.db.base import init_db
from app.services.s3_service import ensure_bucket_exists

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    logger.info("Application starting up")

    init_db()
    logger.info("Database tables verified")

    try:
        await asyncio.to_thread(ensure_bucket_exists)
        logger.info("S3 bucket verified")
    except Exception as exc:
        logger.warning("S3 bucket check failed: %s", exc)

    yield

    logger.info("Application shutting down")

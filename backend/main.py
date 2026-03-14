"""
Ganga Guardian - Smart River Monitoring Platform
FastAPI backend entry point.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import init_db
from routers import sensors, complaints, analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Ganga Guardian backend started")
    yield
    logger.info("Ganga Guardian backend shutting down")


app = FastAPI(
    title="Ganga Guardian API",
    description="Smart environmental monitoring for river pollution and citizen reporting",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


@app.get("/", tags=["Health"])
def health():
    return {"system": "Ganga Guardian Monitoring Active", "status": "healthy"}


app.include_router(sensors.router)
app.include_router(complaints.router)
app.include_router(analytics.router)

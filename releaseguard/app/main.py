"""FastAPI application entry point for the ReleaseGuard test runner.

This module creates the FastAPI app instance. Route modules will be
registered here as Phase 2 endpoints are added.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import builds, test_runs
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="ReleaseGuard",
    description=(
        "Release reliability test runner. Creates builds, runs automated "
        "tests against the fake router service, and records pass/fail results."
    ),
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(builds.router)
app.include_router(test_runs.router)

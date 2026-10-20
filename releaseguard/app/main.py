"""FastAPI application entry point for the ReleaseGuard test runner.

This module creates the FastAPI app instance. Route modules will be
registered here as Phase 2 endpoints are added.
"""

from fastapi import FastAPI

app = FastAPI(
    title="ReleaseGuard",
    description=(
        "Release reliability test runner. Creates builds, runs automated "
        "tests against the fake router service, and records pass/fail results."
    ),
    version="0.1.0",
)

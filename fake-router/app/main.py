"""FastAPI application entry point for the ReleaseGuard Fake Router Service.

This module creates the FastAPI app instance and will register
all route modules (health, devices, firmware, admin).
"""

from fastapi import FastAPI

from app.routes import admin, health, devices, firmware

app = FastAPI(
    title="ReleaseGuard Fake Router",
    description=(
        "Simulated router/network device API used by ReleaseGuard "
        "to test release reliability under normal and fault conditions."
    ),
    version="0.1.0",
)

app.include_router(admin.router)
app.include_router(health.router)
app.include_router(devices.router)
app.include_router(firmware.router)

from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.schemas.test_run import TestRun, TestRunCreate
from app.services import test_run_service

router = APIRouter()

@router.post("/test-runs")
async def create_test_run(payload: TestRunCreate) -> TestRun:
    test_run = test_run_service.create_test_run(payload)
    if test_run is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return test_run

@router.get("/test-runs/{run_id}")
async def get_test_run(run_id: UUID) -> TestRun:
    test_run = test_run_service.get_test_run(run_id)
    if test_run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    return test_run

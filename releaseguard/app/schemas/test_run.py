from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel


class TestRunCreate(BaseModel):
    build_id: UUID


class TestCaseResult(BaseModel):
    test_name: str
    endpoint: str
    status_code: int | None
    latency_ms: float
    passed: bool
    failure_reason: str | None = None


class TestRun(BaseModel):
    run_id: UUID
    build_id: UUID
    status: Literal["passed", "failed"]
    started_at: datetime
    completed_at: datetime
    results: list[TestCaseResult]

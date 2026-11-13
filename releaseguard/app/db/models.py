from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Build(Base):
    __tablename__ = "builds"

    build_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TestRun(Base):
    __tablename__ = "test_runs"

    run_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    build_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("builds.build_id"))
    suite: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    results: Mapped[list["TestCaseResult"]] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
    )


class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("test_runs.run_id", ondelete="CASCADE")
    )
    test_name: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String)
    expected_result: Mapped[str] = mapped_column(String)
    actual_result: Mapped[str] = mapped_column(String)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float)
    passed: Mapped[bool] = mapped_column(Boolean)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    test_run: Mapped["TestRun"] = relationship(back_populates="results")

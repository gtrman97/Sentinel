"""SQLAlchemy models for Sentinel's core schema.

Five tables per the project plan: test_suites, test_cases, test_runs,
test_results, failure_artifacts. Built one at a time — this is step 1.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TestSuite(Base):
    """A named collection of tests, e.g. 'checkout_flow_suite'.

    This is the top of the hierarchy: a suite contains test_cases,
    and each import run (test_run) belongs to a suite.
    """

    __tablename__ = "test_suites"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class TestCase(Base):
    """A single named test within a suite, e.g. 'test_login_with_valid_credentials'.

    Identity here is (suite_id, name) — the same test name could theoretically
    exist in two different suites and those are different tests.
    """

    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    suite_id: Mapped[int] = mapped_column(ForeignKey("test_suites.id"))
    name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class TestRun(Base):
    """One execution of a suite — i.e. one JUnit XML import.

    All test_results from a single import share one test_run. This is what
    lets us compute flakiness across runs: same test_case, different test_run,
    different outcome.
    """

    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    suite_id: Mapped[int] = mapped_column(ForeignKey("test_suites.id"))
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    environment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

class ResultStatus(enum.Enum):
    """Possible outcomes for a single test result, per JUnit XML semantics."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestResult(Base):
    """The outcome of one test_case within one test_run.

    This is the row the flakiness score is actually computed from:
    for a given test_case, look at its test_results across many test_runs
    and count the status transitions.
    """

    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id"))
    test_run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id"))
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus))
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

class FailureArtifact(Base):
    """A reference to evidence captured for a failed/errored test_result.

    Stores a path or URL, not the file itself — so moving from local disk
    storage (v1/v2) to something like S3 later is a config change, not a
    schema change.
    """

    __tablename__ = "failure_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_result_id: Mapped[int] = mapped_column(ForeignKey("test_results.id"))
    artifact_type: Mapped[str] = mapped_column(String(50))
    path_or_url: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
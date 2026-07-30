"""SQLAlchemy models for Sentinel's core schema.

Five tables per the project plan: test_suites, test_cases, test_runs,
test_results, failure_artifacts. Built one at a time — this is step 1.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
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
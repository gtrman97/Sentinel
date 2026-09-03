"""Import JUnit XML test results into Sentinel's database.

Step A: parsing only, prints what it finds. Step B (next) adds the
actual database writes.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from sentinel.db import get_session
from sentinel.models import ResultStatus, TestCase, TestResult, TestRun, TestSuite

@dataclass
class ParsedResult:
    """One <testcase> entry parsed out of a JUnit XML report."""

    name: str
    classname: str
    duration_seconds: float
    status: str  # "passed", "failed", "error", or "skipped"
    error_message: Optional[str]


def parse_junit_xml(xml_path: Path) -> list[ParsedResult]:
    """Parse a JUnit XML report into a list of ParsedResult objects."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    results: list[ParsedResult] = []

    for testcase in root.iter("testcase"):
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")

        if failure is not None:
            status = "failed"
            error_message = failure.get("message")
        elif error is not None:
            status = "error"
            error_message = error.get("message")
        elif skipped is not None:
            status = "skipped"
            error_message = skipped.get("message")
        else:
            status = "passed"
            error_message = None

        results.append(
            ParsedResult(
                name=testcase.get("name", ""),
                classname=testcase.get("classname", ""),
                duration_seconds=float(testcase.get("time", 0.0)),
                status=status,
                error_message=error_message,
            )
        )

    return results

SUITE_NAME = "sentinel_demo_suite"  # v1 simplification: one suite, hardcoded


def get_or_create_suite(session: Session, name: str) -> TestSuite:
    suite = session.query(TestSuite).filter_by(name=name).first()
    if suite is None:
        suite = TestSuite(name=name)
        session.add(suite)
        session.flush()  # assigns suite.id without committing yet
    return suite


def get_or_create_test_case(session: Session, suite: TestSuite, result: ParsedResult) -> TestCase:
    test_case = (
        session.query(TestCase)
        .filter_by(suite_id=suite.id, name=result.name)
        .first()
    )
    if test_case is None:
        file_path = result.classname.replace(".", "/") + ".py"
        test_case = TestCase(suite_id=suite.id, name=result.name, file_path=file_path)
        session.add(test_case)
        session.flush()
    return test_case


def import_results(xml_path: Path) -> int:
    """Parse a JUnit XML report and write it into the database.

    Every call creates one new TestRun (this is what gives us history to
    score flakiness against) but reuses existing TestSuite/TestCase rows.

    Returns the new TestRun's id, not the ORM object itself — the object
    would be unusable once the session below closes.
    """
    parsed_results = parse_junit_xml(xml_path)

    with get_session() as session:
        suite = get_or_create_suite(session, SUITE_NAME)

        test_run = TestRun(suite_id=suite.id)
        session.add(test_run)
        session.flush()  # assigns test_run.id

        for result in parsed_results:
            test_case = get_or_create_test_case(session, suite, result)
            test_result = TestResult(
                test_case_id=test_case.id,
                test_run_id=test_run.id,
                status=ResultStatus(result.status),
                duration_seconds=result.duration_seconds,
                error_message=result.error_message,
            )
            session.add(test_result)

        session.commit()
        run_id = test_run.id  # grab it now, while still inside the session

    return run_id


if __name__ == "__main__":
    run_id = import_results(Path("reports/junit.xml"))
    print(f"Imported TestRun id={run_id}")
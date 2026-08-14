"""Import JUnit XML test results into Sentinel's database.

Step A: parsing only, prints what it finds. Step B (next) adds the
actual database writes.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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


if __name__ == "__main__":
    parsed = parse_junit_xml(Path("reports/junit.xml"))
    for result in parsed:
        print(result)
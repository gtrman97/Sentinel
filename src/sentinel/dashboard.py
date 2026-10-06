"""Render the bare-bones Sentinel dashboard as a static HTML file.

v1: no FastAPI, no live server — just query the database, compute
scores, and write out a plain .html file you open directly in a browser.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from sentinel.db import get_session
from sentinel.models import ResultStatus, TestCase, TestResult, TestRun
from sentinel.scoring import calculate_flakiness_score


def build_dashboard_data(session: Session) -> list[dict]:
    """Query every test_case and compute its pass rate + flakiness score."""
    test_cases = session.query(TestCase).all()
    rows = []

    for test_case in test_cases:
        # Ordered by test_run_id so statuses are chronological — required
        # for the flakiness score, which cares about the *sequence* of
        # results, not just the count of each.
        results = (
            session.query(TestResult)
            .filter_by(test_case_id=test_case.id)
            .join(TestRun)
            .order_by(TestRun.id)
            .all()
        )
        statuses = [result.status for result in results]

        total_runs = len(statuses)
        passed_count = sum(1 for status in statuses if status == ResultStatus.PASSED)
        pass_rate = passed_count / total_runs if total_runs > 0 else 0.0

        rows.append(
            {
                "name": test_case.name,
                "total_runs": total_runs,
                "pass_rate": pass_rate,
                "flakiness_score": calculate_flakiness_score(statuses),
            }
        )

    return rows


def render_dashboard(output_path: Path) -> None:
    """Build the dashboard data and write it to output_path as HTML."""
    with get_session() as session:
        tests = build_dashboard_data(session)  # plain dicts, safe after session closes

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("dashboard.html")
    html = template.render(tests=tests)
    output_path.write_text(html)


if __name__ == "__main__":
    output_file = Path("dashboard_output.html")
    render_dashboard(output_file)
    print(f"Dashboard written to {output_file}")
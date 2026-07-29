# Sentinel

**Sentinel** watches your Selenium/pytest test suite over time, stores historical run data, and flags flaky tests before they erode trust in your test suite.

Most test dashboards tell you what passed and failed on the *last* run. Sentinel looks across runs to answer a harder question: which of your failures are real regressions, and which are just noise?

## Why

Flaky tests are one of the most corrosive problems in test automation, they quietly train engineers to ignore failures, which means real regressions slip through. Sentinel exists to make flakiness visible, measurable, and trackable instead of anecdotal ("yeah, that test just does that sometimes").

## How it works

```
Selenium/pytest suite (GitHub Actions)
        │
        ▼
JUnit XML + failure screenshots
        │
        ▼
FastAPI importer  ──────►  PostgreSQL
        │                  (test_suites, test_cases,
        │                   test_runs, test_results,
        │                   failure_artifacts)
        ▼
Dashboard (Jinja2 + Chart.js)
  pass rate · duration trends · flakiness score
```

Test runs execute in CI, export JUnit XML, and upload artifacts. Sentinel's importer pulls those results (via the GitHub Actions API or a manual upload endpoint for local runs), normalizes them, and writes them to Postgres. The dashboard reads from Postgres to surface trends a single run can't show you.

## Flakiness scoring

A test isn't labeled "flaky" on a hunch — Sentinel computes a score:

- **Core signal** — a test is a flake candidate if its status changes across runs of the same commit with no code change in between.
- **Flakiness score** — ratio of pass↔fail transitions to total runs over a rolling window (e.g. last 20 runs), producing a 0–1 score rather than a binary label.
- **Environment correlation** — cross-references failures against browser/runner to separate genuine flakiness from reproducible, environment-specific failures.
- **Streak detection** — tracks consecutive pass/fail streaks to distinguish an isolated blip from a real regression trending toward consistent failure.
- **Confidence threshold** — a test needs a minimum number of runs (default: 5) before it's scored, to avoid false positives on new tests.

## Tech stack

| Layer | Tools |
|---|---|
| Testing | Python, pytest, Selenium WebDriver, Selenium Manager |
| API | FastAPI, Pydantic |
| Data | PostgreSQL, SQLAlchemy, Alembic |
| Dashboard | Jinja2, Chart.js |
| Packaging / CI | Docker Compose, GitHub Actions |
| Quality | Ruff, mypy, pre-commit, pytest-cov |

## Status

Sentinel is being built in sequenced, independently-demoable milestones:

- [ ] **v1 — Core loop:** local pytest/Selenium runs → JUnit XML → SQLite → flakiness score → bare-bones dashboard
- [ ] **v2 — Real backend:** PostgreSQL + Alembic, FastAPI ingestion endpoints, Chart.js visualizations
- [ ] **v3 — CI integration:** GitHub Actions runs the suite; importer pulls results automatically
- [ ] **v4 — Packaging:** Docker Compose, linting/pre-commit in CI, Makefile, full README + demo

## Getting started

```bash
make setup   # install dependencies, set up local environment
make test    # run the pytest suite
make selenium  # run the Selenium browser tests
make dev     # start the FastAPI + dashboard locally
```

*(Setup instructions will be filled in as v1 lands.)*

## Database schema

- `test_suites` — logical grouping of tests
- `test_cases` — individual test identity, independent of any single run
- `test_runs` — one row per CI/local run, with git commit and CI run ID
- `test_results` — per-test outcome for a given run (status, duration, browser, error, stack trace)
- `failure_artifacts` — screenshot and log references for failed results

## Roadmap

Beyond v4: response comparison across runs, browser comparison views, PR check annotations, API test ingestion, statistical/ML-based flake detection, and multi-project team dashboards.

## License

MIT

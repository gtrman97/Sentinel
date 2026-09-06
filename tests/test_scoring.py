"""Unit tests for flakiness scoring, against known synthetic scenarios."""

from sentinel.models import ResultStatus
from sentinel.scoring import calculate_flakiness_score

PASS = ResultStatus.PASSED
FAIL = ResultStatus.FAILED


def test_returns_none_below_confidence_threshold() -> None:
    """Fewer than 5 runs — not enough history to trust a score."""
    statuses = [PASS, PASS, PASS, FAIL]  # only 4 runs
    assert calculate_flakiness_score(statuses) is None


def test_never_flips_scores_zero() -> None:
    """5 runs, all identical — completely stable, score should be 0.0."""
    statuses = [PASS, PASS, PASS, PASS, PASS]
    assert calculate_flakiness_score(statuses) == 0.0


def test_flips_every_run_scores_one() -> None:
    """Alternates every single run — maximum possible flakiness, score 1.0."""
    statuses = [PASS, FAIL, PASS, FAIL, PASS]
    assert calculate_flakiness_score(statuses) == 1.0


def test_partial_flips_scores_between_zero_and_one() -> None:
    """10 runs, exactly 2 transitions -> score should be 2/9."""
    statuses = [PASS, PASS, PASS, PASS, FAIL, FAIL, FAIL, FAIL, FAIL, PASS]
    # transitions happen at index 3->4 (PASS->FAIL) and 8->9 (FAIL->PASS) = 2
    assert calculate_flakiness_score(statuses) == 2 / 9


def test_only_considers_most_recent_window() -> None:
    """25 runs, but only the last 20 should count toward the score.

    The first 5 runs alternate wildly (would inflate the score if counted),
    but they fall outside the rolling window and should be ignored entirely.
    """
    old_noisy_runs = [PASS, FAIL, PASS, FAIL, PASS]  # outside the window
    recent_stable_runs = [PASS] * 20  # inside the window, zero flips
    statuses = old_noisy_runs + recent_stable_runs

    assert calculate_flakiness_score(statuses) == 0.0
"""Flakiness scoring logic for Sentinel.

Per the plan's methodology: a rolling window of recent runs, scored as
the ratio of status transitions to total transitions possible. Returns
None if there isn't enough run history yet (confidence threshold).
"""

from typing import Optional

from sentinel.models import ResultStatus

ROLLING_WINDOW_SIZE = 20
MIN_RUNS_FOR_CONFIDENCE = 5


def calculate_flakiness_score(statuses: list[ResultStatus]) -> Optional[float]:
    """Calculate a flakiness score from a chronological list of statuses.

    Args:
        statuses: pass/fail statuses for one test_case, ordered oldest to
            newest (i.e. the order they actually ran in).

    Returns:
        A score from 0.0 (never flips) to 1.0 (flips every single run),
        or None if there are fewer than MIN_RUNS_FOR_CONFIDENCE total runs.
    """
    if len(statuses) < MIN_RUNS_FOR_CONFIDENCE:
        return None

    # Only look at the most recent N runs — older history shouldn't
    # dilute a test's *current* flakiness.
    window = statuses[-ROLLING_WINDOW_SIZE:]

    transitions = 0
    for previous, current in zip(window, window[1:]):
        if previous != current:
            transitions += 1

    possible_transitions = len(window) - 1
    return transitions / possible_transitions
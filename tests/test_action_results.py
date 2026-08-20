"""Nav2 terminal result tests."""

import pytest

from warehouse_robot_llm.action_results import classify_action_status


def test_only_succeeded_status_is_success():
    outcomes = {status: classify_action_status(status) for status in range(7)}
    assert outcomes[4].succeeded is True
    assert all(not outcome.succeeded for status, outcome in outcomes.items() if status != 4)


@pytest.mark.parametrize(
    ("status", "label"),
    [(4, "succeeded"), (5, "canceled"), (6, "aborted"), (999, "unrecognized(999)")],
)
def test_status_labels(status, label):
    assert classify_action_status(status).label == label

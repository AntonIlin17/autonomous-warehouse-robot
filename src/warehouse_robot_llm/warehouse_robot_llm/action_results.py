"""Nav2 action-result classification kept independent for unit testing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionOutcome:
    """Human-readable action state with an explicit success flag."""

    label: str
    succeeded: bool


_OUTCOMES = {
    0: ActionOutcome("unknown", False),
    1: ActionOutcome("accepted", False),
    2: ActionOutcome("executing", False),
    3: ActionOutcome("canceling", False),
    4: ActionOutcome("succeeded", True),
    5: ActionOutcome("canceled", False),
    6: ActionOutcome("aborted", False),
}


def classify_action_status(status: int) -> ActionOutcome:
    """Classify an action_msgs/GoalStatus value without treating failure as success."""
    return _OUTCOMES.get(status, ActionOutcome(f"unrecognized({status})", False))

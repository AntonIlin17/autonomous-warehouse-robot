"""Deterministic baseline command parsing tests."""

from pathlib import Path

import pytest

from warehouse_robot_llm.location_registry import LocationRegistry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = LocationRegistry.from_csv(
    ROOT / "src" / "warehouse_robot_nav" / "config" / "locations.csv"
)


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("Go to the loading dock", "loading_area"),
        ("navigate to aisle two", "aisle_2"),
        ("Head to the packing table", "packing_station"),
        ("Return to base", "home"),
        ("CHARGER, please", "charging_station"),
    ],
)
def test_keyword_aliases(command, expected):
    assert REGISTRY.match(command).destination_id == expected


@pytest.mark.parametrize("command", ["", "   ", "the battery is almost dead", "dance in place"])
def test_invalid_or_non_keyword_input_is_not_guessed(command):
    assert REGISTRY.match(command) is None


def test_partial_words_do_not_trigger_destinations():
    assert REGISTRY.match("the homeowner called") is None

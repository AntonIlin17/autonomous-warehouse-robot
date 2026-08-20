"""Small package-local suite executed by colcon test."""

import json
from pathlib import Path

from warehouse_robot_llm.action_results import classify_action_status
from warehouse_robot_llm.location_registry import LocationRegistry
from warehouse_robot_llm.mistral_resolver import MistralResolver


def config_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "warehouse_robot_nav"
        / "config"
        / "locations.csv"
    )


def test_keyword_baseline_and_invalid_input():
    registry = LocationRegistry.from_csv(config_path())
    assert registry.match("go to aisle one").destination_id == "aisle_1"
    assert registry.match("the battery is almost dead") is None


def test_mistral_allow_list_and_nav2_result():
    registry = LocationRegistry.from_csv(config_path())
    content = json.dumps({"location": "charging_station"})
    body = json.dumps({"choices": [{"message": {"content": content}}]})
    resolver = MistralResolver(
        registry,
        api_key="test-only",
        transport=lambda *_: (200, body),
    )
    assert resolver.resolve("the battery is almost dead").destination_id == "charging_station"
    assert classify_action_status(4).succeeded
    assert not classify_action_status(6).succeeded

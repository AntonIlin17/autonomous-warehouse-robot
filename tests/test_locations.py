"""Canonical destination and coordinate tests."""

from pathlib import Path

import pytest

from warehouse_robot_llm.location_registry import LocationRegistry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "src" / "warehouse_robot_nav" / "config" / "locations.csv"

EXPECTED = {
    "loading_area": (3.0, -4.0, 0.0),
    "aisle_1": (-4.75, 0.0, 0.0),
    "aisle_2": (-2.25, 0.0, 0.0),
    "aisle_3": (0.25, 0.0, 0.0),
    "packing_station": (4.5, 5.0, 0.0),
    "charging_station": (5.5, 0.0, 0.0),
    "home": (0.0, 6.0, 3.14159),
}


def test_canonical_coordinates_are_complete_and_stable():
    registry = LocationRegistry.from_csv(CONFIG)
    actual = {
        location.destination_id: (location.x, location.y, location.yaw)
        for location in registry.all()
    }
    assert actual == EXPECTED


def test_world_features_support_approach_pose_interpretation():
    world = (
        ROOT / "src" / "warehouse_robot_sim" / "worlds" / "warehouse.world"
    ).read_text(encoding="utf-8")
    assert '<model name="loading_dock_platform">' in world
    assert "<pose>5.5 -5.5 0.15" in world
    assert '<model name="charging_station">' in world
    assert "<pose>6.5 0 0.3" in world
    assert '<model name="packing_table_1">' in world
    assert "<pose>5.5 4 0.45" in world


def test_duplicate_aliases_are_rejected(tmp_path):
    bad = tmp_path / "locations.csv"
    bad.write_text(
        "id,name,x,y,yaw,aliases,description\n"
        "one,One,0,0,0,shared,first\n"
        "two,Two,1,1,0,shared,second\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="multiple locations"):
        LocationRegistry.from_csv(bad)

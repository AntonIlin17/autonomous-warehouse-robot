"""Launch and configuration behavior checks."""

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_launch_files_are_valid_python_and_use_package_share_paths():
    launch_files = sorted(SRC.glob("*/launch/*.launch.py"))
    assert {path.name for path in launch_files} >= {
        "nav2.launch.py",
        "sim.launch.py",
        "slam.launch.py",
        "view_robot.launch.py",
    }
    for path in launch_files:
        text = path.read_text(encoding="utf-8")
        ast.parse(text, filename=str(path))
        assert "get_package_share_directory" in text
        assert not re.search(r"(?:/home/|/mnt/[a-z]/|[A-Za-z]:\\\\Users\\\\)", text)


def test_canonical_config_is_installed_by_navigation_package():
    cmake = (SRC / "warehouse_robot_nav" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "install(DIRECTORY config launch maps params rviz" in cmake
    assert (SRC / "warehouse_robot_nav" / "config" / "locations.csv").is_file()


def test_map_and_parameters_use_relative_assets_and_static_obstacles():
    map_yaml = (SRC / "warehouse_robot_nav" / "maps" / "warehouse_map.yaml").read_text(
        encoding="utf-8"
    )
    params = (SRC / "warehouse_robot_nav" / "params" / "nav2_params.yaml").read_text(
        encoding="utf-8"
    )
    world = (SRC / "warehouse_robot_sim" / "worlds" / "warehouse.world").read_text(
        encoding="utf-8"
    )
    assert "image: warehouse_map.pgm" in map_yaml
    assert "ObstacleLayer" in params
    for obstacle in ("obstacle_1", "obstacle_2", "obstacle_3"):
        start = world.index(f'<model name="{obstacle}">')
        assert "<static>true</static>" in world[start : start + 100]

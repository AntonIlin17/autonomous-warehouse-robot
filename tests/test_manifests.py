"""ROS package metadata tests."""

from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def package_manifests():
    return sorted(SRC.glob("*/package.xml"))


def test_all_packages_have_publishable_metadata_without_a_license_grant():
    manifests = package_manifests()
    assert len(manifests) == 4
    for manifest in manifests:
        tree = ET.parse(manifest)
        package = tree.getroot()
        assert package.findtext("version") == "1.0.0"
        assert "TODO" not in manifest.read_text(encoding="utf-8")
        assert package.findtext("maintainer") == "Anton Ilin"
        assert package.findtext("license") == "NOASSERTION"


def test_runtime_dependencies_cover_command_and_nav_interfaces():
    llm = ET.parse(SRC / "warehouse_robot_llm" / "package.xml").getroot()
    dependencies = {node.text for node in llm.findall("exec_depend")}
    assert {
        "action_msgs",
        "ament_index_python",
        "geometry_msgs",
        "nav2_msgs",
        "rclpy",
        "warehouse_robot_nav",
    } <= dependencies

    nav = ET.parse(SRC / "warehouse_robot_nav" / "package.xml").getroot()
    nav_dependencies = {node.text for node in nav.findall("depend")}
    assert "ament_index_cpp" in nav_dependencies
    assert "nav2_msgs" in nav_dependencies


def test_repository_intentionally_has_no_license_file():
    candidates = {path.name.lower() for path in ROOT.iterdir() if path.is_file()}
    assert "license" not in candidates
    assert "license.md" not in candidates
    assert "license.txt" not in candidates

"""Course baseline: deterministic keyword navigation interface."""

import rclpy

from .location_registry import LocationRegistry
from .ros_navigation import NavigationClientNode, installed_locations_path, run_interactive


def main(args=None):
    """Run the submitted keyword-matching behavior with corrected Nav2 results."""
    rclpy.init(args=args)
    registry = LocationRegistry.from_csv(installed_locations_path())
    node = NavigationClientNode("keyword_nav_node", registry)

    def resolve(command: str):
        return registry.match(command), "deterministic keyword matching"

    run_interactive(node, resolve, "WAREHOUSE ROBOT - COURSE KEYWORD BASELINE")


if __name__ == "__main__":
    main()

"""Portfolio enhancement: allow-listed Mistral intent resolution."""

import rclpy

from .location_registry import LocationRegistry
from .mistral_resolver import HybridResolver, MistralResolver
from .ros_navigation import NavigationClientNode, installed_locations_path, run_interactive


def main(args=None):
    """Run the optional Mistral resolver without persisting credentials."""
    rclpy.init(args=args)
    registry = LocationRegistry.from_csv(installed_locations_path())
    node = NavigationClientNode("mistral_nav_node", registry)
    resolver = HybridResolver(registry, MistralResolver(registry))

    def resolve(command: str):
        resolution = resolver.resolve(command)
        if resolution.detail:
            node.get_logger().warn(
                f"Mistral unavailable ({resolution.detail}); keyword fallback used"
            )
        return resolution.location, resolution.backend

    run_interactive(node, resolve, "WAREHOUSE ROBOT - MISTRAL PORTFOLIO ENHANCEMENT")


if __name__ == "__main__":
    main()

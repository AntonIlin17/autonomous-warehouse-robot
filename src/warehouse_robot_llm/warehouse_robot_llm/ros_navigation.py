"""Shared ROS 2 navigation client for the command interfaces."""

from __future__ import annotations

import math
import threading
from pathlib import Path
from typing import Callable

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

from .action_results import classify_action_status
from .location_registry import Location, LocationRegistry


def installed_locations_path() -> Path:
    """Return the installed canonical location configuration."""
    share = Path(get_package_share_directory("warehouse_robot_nav"))
    return share / "config" / "locations.csv"


class NavigationClientNode(Node):
    """Send named destinations to Nav2 and report the actual terminal result."""

    def __init__(self, node_name: str, registry: LocationRegistry):
        super().__init__(node_name)
        self.registry = registry
        self._action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.last_outcome = None

    def send_location(self, location: Location) -> bool:
        """Submit a goal when the action server is available."""
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Nav2 action server is not available")
            return False

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = location.x
        goal.pose.pose.position.y = location.y
        goal.pose.pose.orientation.z = math.sin(location.yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(location.yaw / 2.0)

        self.last_outcome = None
        self.get_logger().info(
            f"Sending {location.name}: x={location.x:.2f}, y={location.y:.2f}, "
            f"yaw={location.yaw:.2f}"
        )
        future = self._action_client.send_goal_async(goal)
        future.add_done_callback(
            lambda response, target=location.name: self._goal_response(response, target)
        )
        return True

    def _goal_response(self, future, target: str) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:  # pragma: no cover - ROS transport failure
            self.get_logger().error(f"Goal submission failed for {target}: {exc}")
            return
        if not goal_handle.accepted:
            self.get_logger().error(f"Nav2 rejected the goal for {target}")
            return

        self.get_logger().info(f"Nav2 accepted the goal for {target}")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda result, name=target: self._goal_result(result, name)
        )

    def _goal_result(self, future, target: str) -> None:
        try:
            status = int(future.result().status)
        except Exception as exc:  # pragma: no cover - ROS transport failure
            self.get_logger().error(f"Could not read Nav2 result for {target}: {exc}")
            return

        self.last_outcome = classify_action_status(status)
        if self.last_outcome.succeeded:
            self.get_logger().info(f"Nav2 reached {target} successfully")
        else:
            self.get_logger().error(
                f"Navigation to {target} ended as {self.last_outcome.label}"
            )


def run_interactive(
    node: NavigationClientNode,
    resolve: Callable[[str], tuple[Location | None, str]],
    heading: str,
) -> None:
    """Run a terminal interface while ROS callbacks spin in the background."""
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    print("\n" + "=" * 60)
    print(heading)
    print("Type a destination request, 'list', or 'quit'.")
    print("=" * 60)
    try:
        while rclpy.ok():
            try:
                command = input("Command> ").strip()
            except EOFError:
                break
            if not command:
                continue
            if command.lower() in {"quit", "exit", "q"}:
                break
            if command.lower() in {"list", "locations", "help"}:
                for location in node.registry.all():
                    print(
                        f"  {location.name:<18} "
                        f"({location.x:+.2f}, {location.y:+.2f}, yaw={location.yaw:.2f})"
                    )
                continue

            location, backend = resolve(command)
            if location is None:
                print("No allow-listed destination matched that request.")
                continue
            print(f"Resolved by {backend}: {location.name}")
            node.send_location(location)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

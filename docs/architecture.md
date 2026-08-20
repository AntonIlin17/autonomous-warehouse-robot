# Architecture

## Runtime data flow

Gazebo Harmonic loads the SDF warehouse and a Xacro-generated differential-drive robot. `ros_gz_bridge` carries LiDAR, odometry, velocity commands, clock, and transform messages between Gazebo and ROS 2. Robot State Publisher supplies the URDF transform chain.

The map server publishes the manually created occupancy map. AMCL estimates `map -> odom`; odometry and the robot model complete the transform tree. Nav2's behavior-tree navigator coordinates the planner, controller, costmaps, behaviors, and velocity smoother.

Every command interface sends the standard `nav2_msgs/action/NavigateToPose` action. Each client separately reports goal rejection and terminal `SUCCEEDED`, `CANCELED`, `ABORTED`, or unknown results.

## Location contract

`src/warehouse_robot_nav/config/locations.csv` is the single source of truth for destination IDs, display names, goal poses, aliases, and descriptions.

The goal poses are approach locations, not the centers of physical models:

| Destination | Goal pose | Physical fixture |
| --- | --- | --- |
| Loading Area | `(3.0, -4.0, 0.0)` | Dock centered near `(5.5, -5.5)` |
| Packing Station | `(4.5, 5.0, 0.0)` | Tables centered near `(5.5, 4.0)` and `(5.5, 6.0)` |
| Charging Station | `(5.5, 0.0, 0.0)` | Charger centered near `(6.5, 0.0)` |

This reconciles the original source conflict without directing the robot into collision geometry.

## Command resolution

The course baseline normalizes text and performs longest-first, word-boundary matching against canonical names and aliases. It does not call an LLM.

The portfolio enhancement sends unmatched intent to Mistral, requests a small JSON object, and canonicalizes the response through the same registry. Only allow-listed destinations can become Nav2 goals. Typed timeout, transport, authorization, and schema failures are safe fallback conditions.

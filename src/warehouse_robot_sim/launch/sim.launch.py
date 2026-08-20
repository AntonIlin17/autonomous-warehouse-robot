import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    sim_pkg  = get_package_share_directory("warehouse_robot_sim")
    desc_pkg = get_package_share_directory("warehouse_robot_description")
    world_file = os.path.join(sim_pkg, "worlds", "warehouse.world")
    urdf_file  = os.path.join(desc_pkg, "urdf", "robot.urdf.xacro")
    robot_description = Command(["xacro ", urdf_file])

    return LaunchDescription([
        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_file],
            additional_env={"LIBGL_ALWAYS_SOFTWARE": "1"},
            output="screen"
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": robot_description,
                "use_sim_time": True
            }]
        ),
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package="ros_gz_sim",
                    executable="create",
                    arguments=[
                        "-name", "warehouse_robot",
                        "-topic", "robot_description",
                        "-x", "0.0",
                        "-y", "6.0",
                        "-z", "0.15",
                        "-Y", "3.14159",
                    ],
                    output="screen"
                ),
            ]
        ),
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package="ros_gz_bridge",
                    executable="parameter_bridge",
                    arguments=[
                        "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
                        "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
                        "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
                        "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                        "/model/warehouse_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
                    ],
                    remappings=[
                        ("/model/warehouse_robot/tf", "/tf"),
                    ],
                    output="screen"
                ),
            ]
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="lidar_frame_fix",
            arguments=["0", "0", "0", "0", "0", "0", "laser_frame", "warehouse_robot/base_footprint/lidar"],
            output="screen"
        ),
    ])

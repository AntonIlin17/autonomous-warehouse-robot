import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    nav_pkg = get_package_share_directory("warehouse_robot_nav")
    slam_params = os.path.join(nav_pkg, "params", "slam_params.yaml")

    return LaunchDescription([

        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[
                slam_params,
                {"use_sim_time": True}
            ],
            remappings=[
                ("/tf", "/tf"),
                ("/tf_static", "/tf_static"),
            ]
        ),

        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            parameters=[{"use_sim_time": True}],
        ),

    ])

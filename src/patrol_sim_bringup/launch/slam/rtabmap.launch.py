"""RTAB-Map 适配器，使用仿真提供的里程计和二维激光。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("rtabmap_params_file", description="RTAB-Map 参数文件。"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("scan_topic", default_value="/scan"),
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("base_frame", default_value="base_footprint"),
            Node(
                package="rtabmap_slam",
                executable="rtabmap",
                name="rtabmap",
                parameters=[
                    LaunchConfiguration("rtabmap_params_file"),
                    {
                        "use_sim_time": LaunchConfiguration("use_sim_time"),
                        "frame_id": LaunchConfiguration("base_frame"),
                        "odom_frame_id": LaunchConfiguration("odom_frame"),
                        "map_frame_id": LaunchConfiguration("map_frame"),
                    },
                ],
                remappings=[
                    ("scan", LaunchConfiguration("scan_topic")),
                    ("odom", "/odom"),
                ],
                output="screen",
            ),
        ]
    )

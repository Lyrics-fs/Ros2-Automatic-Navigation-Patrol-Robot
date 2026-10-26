"""Cartographer 适配器。

Cartographer 的传感器配置位于 Lua 文件中，因此通过启动参数传入配置
目录和文件名。该适配器不依赖 TurtleBot3 的 Cartographer 启动文件。
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "cartographer_config_directory", description="Cartographer Lua 配置目录。"
            ),
            DeclareLaunchArgument(
                "cartographer_config_basename", description="Cartographer Lua 配置文件名。"
            ),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("scan_topic", default_value="/scan"),
            # 这些参数构成统一接口，实际 frame 名称由 Lua 配置读取。
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("base_frame", default_value="base_footprint"),
            Node(
                package="cartographer_ros",
                executable="cartographer_node",
                name="cartographer_node",
                arguments=[
                    "-configuration_directory",
                    LaunchConfiguration("cartographer_config_directory"),
                    "-configuration_basename",
                    LaunchConfiguration("cartographer_config_basename"),
                ],
                remappings=[("scan", LaunchConfiguration("scan_topic"))],
                parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
                output="screen",
            ),
            Node(
                package="cartographer_ros",
                executable="cartographer_occupancy_grid_node",
                name="cartographer_occupancy_grid_node",
                arguments=["-resolution", "0.05", "-publish_period_sec", "1.0"],
                parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
                output="screen",
            ),
        ]
    )

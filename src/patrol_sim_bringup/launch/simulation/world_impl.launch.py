"""Gazebo 世界启动实现。

该文件只负责加载世界和 Gazebo 客户端，不负责机器人模型、TF 或传感器。
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gazebo_ros = FindPackageShare("gazebo_ros")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("patrol_sim_bringup"), "worlds", "turtlebot3_world.world"]
                ),
                description="Gazebo 世界文件路径。",
            ),
            DeclareLaunchArgument(
                "use_gui",
                default_value="true",
                description="是否启动 Gazebo 图形客户端。",
            ),
            SetEnvironmentVariable(
                "GAZEBO_MODEL_PATH",
                [
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "models"]
                    ),
                    ":",
                    EnvironmentVariable("GAZEBO_MODEL_PATH", default_value=""),
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([gazebo_ros, "launch", "gzserver.launch.py"])
                ),
                launch_arguments={"world": LaunchConfiguration("world")}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([gazebo_ros, "launch", "gzclient.launch.py"])
                ),
                condition=IfCondition(LaunchConfiguration("use_gui")),
            ),
        ]
    )

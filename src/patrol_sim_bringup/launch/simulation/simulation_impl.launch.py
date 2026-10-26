"""仿真组合入口。

世界和机器人分别由独立启动文件提供，本文件只负责把两者组合起来。
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_share = FindPackageShare("patrol_sim_bringup")
    names = {
        "model": "burger",
        "world": PathJoinSubstitution([package_share, "worlds", "turtlebot3_world.world"]),
        "use_gui": "true",
        "robot_urdf_file": "",
        "robot_sdf_file": "",
        "entity_name": "",
        "x_pose": "-2.0",
        "y_pose": "-0.5",
        "use_camera": "true",
    }
    robot_names = tuple(name for name in names if name not in ("world", "use_gui"))
    return LaunchDescription(
        [
            *[DeclareLaunchArgument(name, default_value=value) for name, value in names.items()],
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [package_share, "launch", "simulation", "world_impl.launch.py"]
                    )
                ),
                launch_arguments={
                    "world": LaunchConfiguration("world"),
                    "use_gui": LaunchConfiguration("use_gui"),
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [package_share, "launch", "simulation", "robot_impl.launch.py"]
                    )
                ),
                launch_arguments={
                    name: LaunchConfiguration(name) for name in robot_names
                }.items(),
            ),
        ]
    )

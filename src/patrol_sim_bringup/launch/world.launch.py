"""独立世界公开入口；机器人模型不会随该入口启动。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("patrol_sim_bringup"), "worlds", "turtlebot3_world.world"]
                ),
                description="Gazebo 世界文件路径。",
            ),
            DeclareLaunchArgument("use_gui", default_value="true"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "simulation", "world_impl.launch.py"]
                    )
                ),
                launch_arguments={
                    "world": LaunchConfiguration("world"),
                    "use_gui": LaunchConfiguration("use_gui"),
                }.items(),
            ),
        ]
    )

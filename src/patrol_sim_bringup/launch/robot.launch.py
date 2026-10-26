"""独立机器人公开入口；需要先启动 Gazebo 世界。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    names = {
        "model": "burger",
        "robot_urdf_file": "",
        "robot_sdf_file": "",
        "entity_name": "",
        "x_pose": "-2.0",
        "y_pose": "-0.5",
        "use_camera": "true",
    }
    return LaunchDescription(
        [
            *[DeclareLaunchArgument(name, default_value=value) for name, value in names.items()],
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "simulation", "robot_impl.launch.py"]
                    )
                ),
                launch_arguments={name: LaunchConfiguration(name) for name in names}.items(),
            ),
        ]
    )

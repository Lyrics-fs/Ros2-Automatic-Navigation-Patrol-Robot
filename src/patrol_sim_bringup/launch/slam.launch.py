"""SLAM 公开入口；具体调度器位于 launch/slam/。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    names = {
        "slam_backend": "slam_toolbox",
        "slam_launch_file": "",
        "slam_params_file": PathJoinSubstitution([FindPackageShare("patrol_sim_bringup"), "config", "slam", "slam_toolbox.yaml"]),
        "scan_topic": "/scan",
        "map_frame": "map",
        "odom_frame": "odom",
        "base_frame": "base_footprint",
        "cartographer_config_directory": "",
        "cartographer_config_basename": "",
        "rtabmap_params_file": PathJoinSubstitution([FindPackageShare("patrol_sim_bringup"), "config", "slam", "rtabmap.yaml"]),
        "use_sim_time": "true",
        "use_rviz": "true",
    }
    declarations = [DeclareLaunchArgument(name, default_value=value) for name, value in names.items()]
    return LaunchDescription(
        declarations
        + [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "slam", "slam.launch.py"]
                    )
                ),
                launch_arguments={name: LaunchConfiguration(name) for name in names}.items(),
            )
        ]
    )

"""导航公开入口；具体实现位于 launch/navigation/。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    names = {
        "map": PathJoinSubstitution(
            [FindPackageShare("patrol_sim_bringup"), "maps", "slam_toolbox", "patrol_map.yaml"]
        ),
        "params_file": PathJoinSubstitution([FindPackageShare("turtlebot3_navigation2"), "param", "humble", "burger.yaml"]),
        "planner": "navfn",
        "planner_config_file": "",
        "controller": "dwb",
        "controller_config_file": "",
        "use_sim_time": "true",
        "autostart": "true",
        "use_rviz": "true",
        "auto_initialize_pose": "true",
        "initial_pose_x": "-2.0",
        "initial_pose_y": "-0.5",
        "initial_pose_yaw": "0.0",
    }
    declarations = [DeclareLaunchArgument(name, default_value=value) for name, value in names.items()]
    return LaunchDescription(
        declarations
        + [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "navigation", "navigation_impl.launch.py"]
                    )
                ),
                launch_arguments={name: LaunchConfiguration(name) for name in names}.items(),
            )
        ]
    )

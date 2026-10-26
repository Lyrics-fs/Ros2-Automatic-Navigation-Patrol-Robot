"""仿真公开入口；具体实现位于 launch/simulation/。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value="burger"),
            DeclareLaunchArgument("x_pose", default_value="-2.0"),
            DeclareLaunchArgument("y_pose", default_value="-0.5"),
            DeclareLaunchArgument("use_camera", default_value="true"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "simulation", "simulation.launch.py"]
                    )
                ),
                launch_arguments={
                    "model": LaunchConfiguration("model"),
                    "x_pose": LaunchConfiguration("x_pose"),
                    "y_pose": LaunchConfiguration("y_pose"),
                    "use_camera": LaunchConfiguration("use_camera"),
                }.items(),
            ),
        ]
    )

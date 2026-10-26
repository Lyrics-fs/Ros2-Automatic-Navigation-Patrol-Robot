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
            DeclareLaunchArgument(
                "world",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("patrol_sim_bringup"), "worlds", "turtlebot3_world.world"]
                ),
            ),
            DeclareLaunchArgument("use_gui", default_value="true"),
            DeclareLaunchArgument("robot_urdf_file", default_value=""),
            DeclareLaunchArgument("robot_sdf_file", default_value=""),
            DeclareLaunchArgument("entity_name", default_value=""),
            DeclareLaunchArgument("x_pose", default_value="-2.0"),
            DeclareLaunchArgument("y_pose", default_value="-0.5"),
            DeclareLaunchArgument("use_camera", default_value="true"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("patrol_sim_bringup"), "launch", "simulation", "simulation_impl.launch.py"]
                    )
                ),
                launch_arguments={
                    "model": LaunchConfiguration("model"),
                    "world": LaunchConfiguration("world"),
                    "use_gui": LaunchConfiguration("use_gui"),
                    "x_pose": LaunchConfiguration("x_pose"),
                    "y_pose": LaunchConfiguration("y_pose"),
                    "use_camera": LaunchConfiguration("use_camera"),
                    "robot_urdf_file": LaunchConfiguration("robot_urdf_file"),
                    "robot_sdf_file": LaunchConfiguration("robot_sdf_file"),
                    "entity_name": LaunchConfiguration("entity_name"),
                }.items(),
            ),
        ]
    )

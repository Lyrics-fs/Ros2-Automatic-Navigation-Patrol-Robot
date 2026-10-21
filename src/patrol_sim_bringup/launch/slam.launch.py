from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_share = FindPackageShare("patrol_sim_bringup")
    params_file = LaunchConfiguration("slam_params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_rviz = LaunchConfiguration("use_rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "slam_params_file",
                default_value=PathJoinSubstitution(
                    [package_share, "config", "slam_toolbox.yaml"]
                ),
                description="SLAM Toolbox parameter file.",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time.",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Start RViz with the mapping view.",
            ),
            # SLAM Toolbox publishes map -> odom while Gazebo provides odom -> base_footprint.
            Node(
                package="slam_toolbox",
                executable="async_slam_toolbox_node",
                name="slam_toolbox",
                parameters=[params_file, {"use_sim_time": use_sim_time}],
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="slam_rviz",
                arguments=[
                    "-d",
                    PathJoinSubstitution([package_share, "rviz", "slam.rviz"]),
                ],
                condition=IfCondition(use_rviz),
                parameters=[{"use_sim_time": use_sim_time}],
                output="screen",
            ),
        ]
    )

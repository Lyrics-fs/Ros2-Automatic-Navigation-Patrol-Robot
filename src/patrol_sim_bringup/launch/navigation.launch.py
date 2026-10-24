from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    project_share = FindPackageShare("patrol_sim_bringup")
    nav2_share = FindPackageShare("nav2_bringup")
    turtlebot_nav_share = FindPackageShare("turtlebot3_navigation2")

    map_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    use_rviz = LaunchConfiguration("use_rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "map",
                default_value=PathJoinSubstitution(
                    [project_share, "maps", "patrol_map.yaml"]
                ),
                description="Saved occupancy grid YAML file.",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [turtlebot_nav_share, "param", "humble", "burger.yaml"]
                ),
                description="TurtleBot3 Burger Nav2 parameters for Humble.",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time.",
            ),
            DeclareLaunchArgument(
                "autostart",
                default_value="true",
                description="Automatically activate Nav2 lifecycle nodes.",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Start the Nav2 RViz interface.",
            ),
            # Use Nav2's standard bringup for map_server, AMCL, planner and controller.
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([nav2_share, "launch", "bringup_launch.py"])
                ),
                launch_arguments={
                    "map": map_file,
                    "params_file": params_file,
                    "use_sim_time": use_sim_time,
                    "autostart": autostart,
                    "use_composition": "False",
                }.items(),
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="nav2_rviz",
                arguments=[
                    "-d",
                    PathJoinSubstitution(
                        [turtlebot_nav_share, "rviz", "tb3_navigation2.rviz"]
                    ),
                ],
                condition=IfCondition(use_rviz),
                parameters=[{"use_sim_time": use_sim_time}],
                output="screen",
            ),
        ]
    )

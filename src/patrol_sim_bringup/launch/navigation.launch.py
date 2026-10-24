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
    auto_initialize_pose = LaunchConfiguration("auto_initialize_pose")
    initial_pose_x = LaunchConfiguration("initial_pose_x")
    initial_pose_y = LaunchConfiguration("initial_pose_y")
    initial_pose_yaw = LaunchConfiguration("initial_pose_yaw")

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
            DeclareLaunchArgument(
                "auto_initialize_pose",
                default_value="true",
                description="Publish the initial AMCL pose after AMCL becomes active.",
            ),
            DeclareLaunchArgument(
                "initial_pose_x",
                default_value="-2.0",
                description="Initial robot x position in the map frame.",
            ),
            DeclareLaunchArgument(
                "initial_pose_y",
                default_value="-0.5",
                description="Initial robot y position in the map frame.",
            ),
            DeclareLaunchArgument(
                "initial_pose_yaw",
                default_value="0.0",
                description="Initial robot yaw in radians in the map frame.",
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
            # Wait for AMCL's lifecycle state before sending the pose to avoid a startup race.
            Node(
                package="patrol_sim_bringup",
                executable="initial_pose_publisher.py",
                name="initial_pose_publisher",
                condition=IfCondition(auto_initialize_pose),
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "initial_pose_x": initial_pose_x,
                        "initial_pose_y": initial_pose_y,
                        "initial_pose_yaw": initial_pose_yaw,
                    }
                ],
                output="screen",
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

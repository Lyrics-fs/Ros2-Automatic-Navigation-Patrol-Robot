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
                    [project_share, "maps", "slam_toolbox", "patrol_map.yaml"]
                ),
                description="已保存的栅格地图 YAML 文件。",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [turtlebot_nav_share, "param", "humble", "burger.yaml"]
                ),
                description="适用于 Humble 的 TurtleBot3 Burger Nav2 参数文件。",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="使用 Gazebo 仿真时间。",
            ),
            DeclareLaunchArgument(
                "autostart",
                default_value="true",
                description="自动激活 Nav2 生命周期节点。",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="启动 Nav2 的 RViz 界面。",
            ),
            DeclareLaunchArgument(
                "auto_initialize_pose",
                default_value="true",
                description="AMCL 激活后发布初始位姿。",
            ),
            DeclareLaunchArgument(
                "initial_pose_x",
                default_value="-2.0",
                description="机器人在 map 坐标系中的初始 x 坐标。",
            ),
            DeclareLaunchArgument(
                "initial_pose_y",
                default_value="-0.5",
                description="机器人在 map 坐标系中的初始 y 坐标。",
            ),
            DeclareLaunchArgument(
                "initial_pose_yaw",
                default_value="0.0",
                description="机器人在 map 坐标系中的初始偏航角，单位为弧度。",
            ),
            # 使用 Nav2 标准启动文件加载地图服务、AMCL、规划器和控制器。
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
            # 等待 AMCL 生命周期节点激活后再发送位姿，避免启动时序冲突。
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

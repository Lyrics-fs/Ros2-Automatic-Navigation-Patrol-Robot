from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 直接复用官方世界与 Gazebo 机器人插件，避免维护重复的仿真模型。
    gazebo_share = FindPackageShare("turtlebot3_gazebo")
    upstream_launch = PathJoinSubstitution(
        [gazebo_share, "launch", "turtlebot3_world.launch.py"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "x_pose",
                default_value="-2.0",
                description="Initial robot x position in the world.",
            ),
            DeclareLaunchArgument(
                "y_pose",
                default_value="-0.5",
                description="Initial robot y position in the world.",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(upstream_launch),
                # Gazebo 和节点统一使用仿真时钟，初始位置可由上层参数覆盖。
                launch_arguments={
                    "x_pose": LaunchConfiguration("x_pose"),
                    "y_pose": LaunchConfiguration("y_pose"),
                    "use_sim_time": "true",
                }.items(),
            ),
        ]
    )

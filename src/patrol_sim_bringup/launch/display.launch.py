from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 模型文件和 RViz 配置均从官方描述包读取，默认显示 Burger。
    model = LaunchConfiguration("model")
    use_rviz = LaunchConfiguration("use_rviz")
    description_share = FindPackageShare("turtlebot3_description")
    model_path = PathJoinSubstitution(
        [description_share, "urdf", ["turtlebot3_", model, ".urdf"]]
    )
    rviz_config = PathJoinSubstitution([description_share, "rviz", "model.rviz"])

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value="burger",
                description="TurtleBot3 model name.",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Start RViz for visual inspection.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                parameters=[{"robot_description": Command(["xacro ", model_path])}],
                output="screen",
            ),
            Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
                name="joint_state_publisher",
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", rviz_config],
                condition=IfCondition(use_rviz),
                output="screen",
            ),
        ]
    )

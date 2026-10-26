from pathlib import Path
# 读取和修改 URDF/SDF XML 文件
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _burger_description_with_camera():
    # 沿用官方 Burger URDF，只补充相机坐标系，供图像消息与 TF 对齐。
    urdf_path = (
        Path(get_package_share_directory("turtlebot3_gazebo"))
        / "urdf"
        / "turtlebot3_burger.urdf"
    )
    robot = ET.parse(urdf_path).getroot()
    ET.SubElement(robot, "link", name="camera_link")
    mount = ET.SubElement(robot, "joint", name="camera_joint", type="fixed")
    ET.SubElement(mount, "parent", link="base_link")
    ET.SubElement(mount, "child", link="camera_link")
    ET.SubElement(mount, "origin", xyz="0.08 0 0.12", rpy="0 0 0")

    ET.SubElement(robot, "link", name="camera_optical_frame")
    optical = ET.SubElement(robot, "joint", name="camera_optical_joint", type="fixed")
    ET.SubElement(optical, "parent", link="camera_link")
    ET.SubElement(optical, "child", link="camera_optical_frame")
    ET.SubElement(
        optical,
        "origin",
        xyz="0 0 0",
        rpy="-1.57079632679 0 -1.57079632679",
    )
    return ET.tostring(robot, encoding="unicode")


def _start_simulation(context):
    model = LaunchConfiguration("model").perform(context)
    use_camera = LaunchConfiguration("use_camera").perform(context).lower()
    if use_camera not in ("true", "false"):
        raise ValueError("use_camera 只能设置为 true 或 false")

    if model != "burger" or use_camera == "false":
        # 其他型号与关闭相机时，保持官方 TurtleBot3 启动方式。
        return [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("turtlebot3_gazebo"), "launch", "turtlebot3_world.launch.py"]
                    )
                ),
                launch_arguments={
                    "x_pose": LaunchConfiguration("x_pose"),
                    "y_pose": LaunchConfiguration("y_pose"),
                    "use_sim_time": "true",
                }.items(),
            )
        ]

    gazebo_ros = FindPackageShare("gazebo_ros")
    world = PathJoinSubstitution(
        [FindPackageShare("turtlebot3_gazebo"), "worlds", "turtlebot3_world.world"]
    )
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([gazebo_ros, "launch", "gzserver.launch.py"])
            ),
            launch_arguments={"world": world}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([gazebo_ros, "launch", "gzclient.launch.py"])
            )
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[
                {
                    "robot_description": _burger_description_with_camera(),
                    "use_sim_time": True,
                }
            ],
            output="screen",
        ),
        Node(
            package="patrol_sim_bringup",
            executable="spawn_burger_camera.py",
            name="spawn_burger_camera",
            parameters=[
                {
                    "x_pose": LaunchConfiguration("x_pose"),
                    "y_pose": LaunchConfiguration("y_pose"),
                }
            ],
            output="screen",
        ),
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value="burger",
                description="要生成的 TurtleBot3 模型。",
            ),
            DeclareLaunchArgument(
                "x_pose",
                default_value="-2.0",
                description="机器人在世界坐标系中的初始 x 坐标。",
            ),
            DeclareLaunchArgument(
                "y_pose",
                default_value="-0.5",
                description="机器人在世界坐标系中的初始 y 坐标。",
            ),
            DeclareLaunchArgument(
                "use_camera",
                default_value="true",
                description="为 Burger 启用 RGB 相机。",
            ),
            SetEnvironmentVariable("TURTLEBOT3_MODEL", LaunchConfiguration("model")),
            OpaqueFunction(function=_start_simulation),
        ]
    )

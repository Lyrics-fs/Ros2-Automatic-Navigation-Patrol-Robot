"""机器人模型启动实现。

该文件只负责机器人 URDF/SDF、TF、Gazebo 生成和可选相机，不启动世界。
默认路径来自 TurtleBot3 官方资源，也可以通过启动参数替换为外部模型。
"""

from pathlib import Path
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _default_model_files(model):
    if model == "burger":
        project_share = Path(get_package_share_directory("patrol_sim_bringup"))
        return (
            project_share / "description" / "urdf" / "turtlebot3_burger.urdf",
            project_share / "models" / "turtlebot3_burger" / "model.sdf",
        )

    # 其他 TurtleBot3 型号仍从官方资源包读取。
    gazebo_share = Path(get_package_share_directory("turtlebot3_gazebo"))
    return (
        gazebo_share / "urdf" / f"turtlebot3_{model}.urdf",
        gazebo_share / "models" / f"turtlebot3_{model}" / "model.sdf",
    )


def _read_urdf(urdf_file):
    path = Path(urdf_file)
    if not path.is_file():
        raise FileNotFoundError(f"机器人 URDF 文件不存在：{path}")
    return path.read_text()


def _urdf_with_camera(urdf_file):
    """给机器人 URDF 增加相机 TF，传感器本体由 SDF 插件生成。"""
    path = Path(urdf_file)
    if not path.is_file():
        raise FileNotFoundError(f"机器人 URDF 文件不存在：{path}")
    robot = ET.parse(path).getroot()
    if robot.find("./link[@name='base_link']") is None:
        raise RuntimeError("机器人 URDF 中未找到 base_link，无法安装相机 TF")
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


def _start_robot(context):
    model = LaunchConfiguration("model").perform(context).strip()
    use_camera = LaunchConfiguration("use_camera").perform(context).lower()
    if not model:
        raise ValueError("model 不能为空")
    if use_camera not in ("true", "false"):
        raise ValueError("use_camera 只能设置为 true 或 false")

    default_urdf, default_sdf = _default_model_files(model)
    urdf_value = LaunchConfiguration("robot_urdf_file").perform(context).strip()
    sdf_value = LaunchConfiguration("robot_sdf_file").perform(context).strip()
    urdf_file = Path(urdf_value) if urdf_value else default_urdf
    sdf_file = Path(sdf_value) if sdf_value else default_sdf
    entity_name = LaunchConfiguration("entity_name").perform(context).strip() or model
    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")

    actions = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[
                {
                    "robot_description": (
                        _urdf_with_camera(urdf_file)
                        if use_camera == "true"
                        else _read_urdf(urdf_file)
                    ),
                    "use_sim_time": True,
                }
            ],
            output="screen",
        )
    ]

    if use_camera == "true":
        if not sdf_file.is_file():
            raise FileNotFoundError(f"机器人 SDF 文件不存在：{sdf_file}")
        actions.append(
            Node(
                package="patrol_sim_bringup",
                executable="spawn_robot_camera.py",
                name="spawn_robot_camera",
                parameters=[
                    {
                        "x_pose": x_pose,
                        "y_pose": y_pose,
                        "sdf_file": str(sdf_file),
                        "entity_name": entity_name,
                    }
                ],
                output="screen",
            )
        )
    else:
        if not sdf_file.is_file():
            raise FileNotFoundError(f"机器人 SDF 文件不存在：{sdf_file}")
        actions.append(
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                name="spawn_robot",
                arguments=[
                    "-entity",
                    entity_name,
                    "-file",
                    str(sdf_file),
                    "-x",
                    x_pose,
                    "-y",
                    y_pose,
                    "-z",
                    "0.01",
                ],
                output="screen",
            )
        )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value="burger"),
            DeclareLaunchArgument(
                "robot_urdf_file",
                default_value="",
                description="机器人 URDF 文件；为空时根据 model 使用官方资源。",
            ),
            DeclareLaunchArgument(
                "robot_sdf_file",
                default_value="",
                description="机器人 SDF 文件；为空时根据 model 使用官方资源。",
            ),
            DeclareLaunchArgument("entity_name", default_value=""),
            DeclareLaunchArgument("x_pose", default_value="-2.0"),
            DeclareLaunchArgument("y_pose", default_value="-0.5"),
            DeclareLaunchArgument("use_camera", default_value="true"),
            SetEnvironmentVariable("TURTLEBOT3_MODEL", LaunchConfiguration("model")),
            OpaqueFunction(function=_start_robot),
        ]
    )

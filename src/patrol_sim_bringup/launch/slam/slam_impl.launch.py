"""SLAM 公共调度入口。

本文件只负责选择 SLAM 后端和启动公共 RViz。具体算法节点放在同目录的
适配器中，更换算法时不需要修改仿真或 Nav2 启动文件。
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _select_backend(context):
    """根据 slam_backend 选择适配器，并传递统一的公共接口参数。"""
    backend = LaunchConfiguration("slam_backend").perform(context).strip().lower()
    project_share = FindPackageShare("patrol_sim_bringup")
    adapter_files = {
        "slam_toolbox": "slam/slam_toolbox.launch.py",
        "cartographer": "slam/cartographer.launch.py",
        "rtabmap": "slam/rtabmap.launch.py",
    }

    if backend == "external":
        adapter_file = LaunchConfiguration("slam_launch_file").perform(context).strip()
        if not adapter_file:
            raise RuntimeError(
                "slam_backend=external 时必须提供 slam_launch_file:=/绝对路径/启动文件.py"
            )
    elif backend == "cartographer":
        config_directory = LaunchConfiguration(
            "cartographer_config_directory"
        ).perform(context).strip()
        config_basename = LaunchConfiguration(
            "cartographer_config_basename"
        ).perform(context).strip()
        if not config_directory or not config_basename:
            raise RuntimeError(
                "slam_backend=cartographer 时必须同时提供 "
                "cartographer_config_directory 和 cartographer_config_basename"
            )
        adapter_file = PathJoinSubstitution(
            [project_share, "launch", adapter_files[backend]]
        )
    elif backend in adapter_files:
        adapter_file = PathJoinSubstitution(
            [project_share, "launch", adapter_files[backend]]
        )
    else:
        supported = ", ".join([*adapter_files, "external"])
        raise RuntimeError(f"不支持的 slam_backend: {backend}，可选值：{supported}")

    # 先传递所有算法都需要的公共接口，再附加当前后端专属参数。
    launch_arguments = {
        "use_sim_time": LaunchConfiguration("use_sim_time"),
        "scan_topic": LaunchConfiguration("scan_topic"),
        "map_frame": LaunchConfiguration("map_frame"),
        "odom_frame": LaunchConfiguration("odom_frame"),
        "base_frame": LaunchConfiguration("base_frame"),
    }
    if backend == "slam_toolbox":
        launch_arguments["slam_params_file"] = LaunchConfiguration("slam_params_file")
    elif backend == "cartographer":
        launch_arguments.update(
            {
                "cartographer_config_directory": LaunchConfiguration(
                    "cartographer_config_directory"
                ),
                "cartographer_config_basename": LaunchConfiguration(
                    "cartographer_config_basename"
                ),
            }
        )
    elif backend == "rtabmap":
        launch_arguments["rtabmap_params_file"] = LaunchConfiguration(
            "rtabmap_params_file"
        )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(adapter_file),
            launch_arguments=launch_arguments.items(),
        )
    ]


def generate_launch_description():
    package_share = FindPackageShare("patrol_sim_bringup")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "slam_backend",
                default_value="slam_toolbox",
                description="SLAM 后端：slam_toolbox、cartographer、rtabmap 或 external。",
            ),
            DeclareLaunchArgument(
                "slam_launch_file",
                default_value="",
                description="external 后端使用的外部适配器启动文件绝对路径。",
            ),
            DeclareLaunchArgument(
                "slam_params_file",
                default_value=PathJoinSubstitution(
                    [package_share, "config", "slam", "slam_toolbox.yaml"]
                ),
                description="SLAM Toolbox 参数文件。",
            ),
            DeclareLaunchArgument(
                "scan_topic", default_value="/scan", description="二维激光扫描话题。"
            ),
            DeclareLaunchArgument(
                "map_frame", default_value="map", description="地图坐标系名称。"
            ),
            DeclareLaunchArgument(
                "odom_frame", default_value="odom", description="里程计坐标系名称。"
            ),
            DeclareLaunchArgument(
                "base_frame",
                default_value="base_footprint",
                description="机器人基座坐标系名称。",
            ),
            DeclareLaunchArgument(
                "cartographer_config_directory",
                default_value="",
                description="Cartographer Lua 配置目录。",
            ),
            DeclareLaunchArgument(
                "cartographer_config_basename",
                default_value="",
                description="Cartographer Lua 配置文件名。",
            ),
            DeclareLaunchArgument(
                "rtabmap_params_file",
                default_value=PathJoinSubstitution(
                    [package_share, "config", "slam", "rtabmap.yaml"]
                ),
                description="RTAB-Map 参数文件。",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="使用 Gazebo 仿真时间。",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="启动 RViz 并加载建图视图。",
            ),
            OpaqueFunction(function=_select_backend),
            # RViz 只依赖公共 map、scan 和 TF 接口，与具体算法解耦。
            Node(
                package="rviz2",
                executable="rviz2",
                name="slam_rviz",
                arguments=[
                    "-d",
                    PathJoinSubstitution([package_share, "rviz", "slam.rviz"]),
                ],
                condition=IfCondition(LaunchConfiguration("use_rviz")),
                parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
                output="screen",
            ),
        ]
    )

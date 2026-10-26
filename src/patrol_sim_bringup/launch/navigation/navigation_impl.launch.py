import tempfile
from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    project_share = FindPackageShare("patrol_sim_bringup")
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

    planner_profiles = {
        "navfn": "navfn.yaml",
        "smac_2d": "smac_2d.yaml",
        "smac_hybrid": "smac_hybrid.yaml",
        "theta_star": "theta_star.yaml",
    }
    controller_profiles = {
        "dwb": "dwb.yaml",
        "regulated_pure_pursuit": "regulated_pure_pursuit.yaml",
        "mppi": "mppi.yaml",
    }

    def launch_nav2(context):
        planner = LaunchConfiguration("planner").perform(context).strip().lower()
        custom_profile = LaunchConfiguration("planner_config_file").perform(context).strip()
        if custom_profile:
            profile_file = custom_profile
        elif planner in planner_profiles:
            profile_file = PathJoinSubstitution(
                [
                    FindPackageShare("patrol_sim_bringup"),
                    "config",
                    "navigation",
                    "planners",
                    planner_profiles[planner],
                ]
            ).perform(context)
        else:
            choices = ", ".join([*planner_profiles, "custom"])
            raise RuntimeError(f"不支持的 planner: {planner}。可选值：{choices}")

        controller = LaunchConfiguration("controller").perform(context).strip().lower()
        custom_controller = LaunchConfiguration("controller_config_file").perform(context).strip()
        if custom_controller:
            controller_file = custom_controller
        elif controller in controller_profiles:
            controller_file = PathJoinSubstitution(
                [
                    FindPackageShare("patrol_sim_bringup"),
                    "config",
                    "navigation",
                    "controllers",
                    controller_profiles[controller],
                ]
            ).perform(context)
        else:
            choices = ", ".join([*controller_profiles, "custom"])
            raise RuntimeError(
                f"不支持的 controller: {controller}。可选值：{choices}"
            )

        base_file = LaunchConfiguration("params_file").perform(context)
        merged_params = _merge_nav2_params(base_file, profile_file, controller_file)
        nav2_launch = (
            Path(get_package_share_directory("nav2_bringup"))
            / "launch"
            / "bringup_launch.py"
        )
        return [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(nav2_launch)),
                launch_arguments={
                    "map": map_file,
                    "params_file": merged_params,
                    "use_sim_time": use_sim_time,
                    "autostart": autostart,
                    "use_composition": "False",
                }.items(),
            )
        ]

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
                "planner",
                default_value="navfn",
                description="全局规划器：navfn、smac_2d、smac_hybrid、theta_star 或 custom。",
            ),
            DeclareLaunchArgument(
                "planner_config_file",
                default_value="",
                description="自定义全局规划器配置 YAML；需包含 planner_server 参数。",
            ),
            DeclareLaunchArgument(
                "controller",
                default_value="dwb",
                description="局部控制器：dwb、regulated_pure_pursuit、mppi 或 custom。",
            ),
            DeclareLaunchArgument(
                "controller_config_file",
                default_value="",
                description="自定义局部控制器配置 YAML；需包含 controller_server 参数。",
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
            # 先合并所选全局规划器配置，再交给 Nav2 标准启动流程。
            OpaqueFunction(function=launch_nav2),
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


def _merge_nav2_params(base_file, planner_file, controller_file):
    """合并全局规划器和局部控制器 profile，再生成 Nav2 临时参数文件。"""
    with open(base_file, "r", encoding="utf-8") as stream:
        base = yaml.safe_load(stream)
    _merge_plugin_section(base, planner_file, "planner_server", "planner_plugins")
    _merge_plugin_section(base, controller_file, "controller_server", "controller_plugins")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", prefix="patrol_nav2_", delete=False
    ) as stream:
        yaml.safe_dump(base, stream, sort_keys=False)
        merged_file = stream.name
    return merged_file


def _merge_plugin_section(base, profile_file, node_name, plugin_list_key):
    with open(profile_file, "r", encoding="utf-8") as stream:
        profile = yaml.safe_load(stream)
    try:
        base_params = base[node_name]["ros__parameters"]
        plugin_params = profile[node_name]["ros__parameters"]
        plugin_ids = plugin_params[plugin_list_key]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(
            f"配置必须包含 {node_name}.ros__parameters.{plugin_list_key}"
        ) from exc
    if not isinstance(plugin_ids, list) or not plugin_ids:
        raise RuntimeError(f"{plugin_list_key} 必须是非空列表")
    for plugin_id in plugin_ids:
        plugin_config = plugin_params.get(plugin_id)
        if not isinstance(plugin_config, dict) or "plugin" not in plugin_config:
            raise RuntimeError(f"插件 {plugin_id} 缺少 plugin 类配置")

    for plugin_id in base_params.get(plugin_list_key, []):
        base_params.pop(plugin_id, None)
    base_params.update(plugin_params)

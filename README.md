# ROS 2 移动机器人自主导航巡逻系统

本项目基于 ROS 2 Humble 和 Gazebo Classic，使用 TurtleBot3 Burger 搭建移动机器人自主导航与巡逻仿真，计划逐步完成 SLAM 建图、Nav2 定位与导航、巡逻点任务和 rosbag 实验复现。

机器人 URDF、Gazebo 模型及仿真世界来自官方 `turtlebot3_description` 和 `turtlebot3_gazebo` ROS 包。本仓库通过启动文件组合这些资源，不复制或维护上游模型副本。

## 当前进度

- 已选用 TurtleBot3 Burger 作为仿真底盘。
- `patrol_sim_bringup` 提供项目自己的模型显示和 Gazebo 仿真入口。
- SLAM Toolbox 在线异步建图入口与 Burger 参数已加入。
- 后续步骤：在可运行 Gazebo 的环境中验收地图，再进入 Nav2 定位与导航。

## 环境依赖

- ROS 2 Humble
- Gazebo Classic
- `ros-humble-turtlebot3`
- `ros-humble-turtlebot3-gazebo`
- `ros-humble-turtlebot3-description`
- `ros-humble-robot-state-publisher`、`ros-humble-rviz2` 和 `ros-humble-xacro`

## 构建工作区

```bash
cd /home/lyrics/Ros2-Automatic-Navigation-Patrol-Robot
source /opt/ros/humble/setup.zsh
colcon build --symlink-install
source install/setup.zsh
```

## 启动 Gazebo 仿真

```bash
ros2 launch patrol_sim_bringup simulation.launch.py
```

项目启动文件会默认选择 Burger，并调用 TurtleBot3 官方 `turtlebot3_world.launch.py`，默认将机器人放置在 `x=-2.0, y=-0.5`。可以用 `model`、`x_pose` 和 `y_pose` 覆盖模型与初始位置：

```bash
ros2 launch patrol_sim_bringup simulation.launch.py model:=burger x_pose:=0.0 y_pose:=0.0
```

## 单独查看机器人模型

不启动 Gazebo，只通过官方 URDF 在 RViz 中查看机器人：

```bash
ros2 launch patrol_sim_bringup display.launch.py
```

无图形界面时可以关闭 RViz，只检查机器人模型解析和状态发布节点：

```bash
ros2 launch patrol_sim_bringup display.launch.py use_rviz:=false
```

## 仿真接口验收

Gazebo 启动后，在另一个终端加载 ROS 和工作区环境，再检查以下话题与 TF：

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 topic list | rg '^/(scan|odom|cmd_vel|clock)$'
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

确认 `/scan`、`/odom`、`/clock` 和 `odom -> base_link` 正常后，再启动下方的 SLAM 建图流程。

## SLAM 建图

先在一个终端启动 Gazebo 仿真。在第二个终端启动在线异步建图：

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 launch patrol_sim_bringup slam.launch.py
```

第三个终端启动键盘遥控，然后缓慢驾驶机器人探索环境；尽量覆盖走廊和房间，并适当回到已走过的区域形成闭环：

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 run turtlebot3_teleop teleop_keyboard
```

RViz 中应逐渐出现 `/map` 栅格地图，激光点云应与地图墙面基本重合。建图完成后在工作区根目录保存地图：

```bash
ros2 run nav2_map_server map_saver_cli -f src/patrol_sim_bringup/maps/patrol_map
```

命令成功后应生成 `patrol_map.yaml` 和 `patrol_map.pgm`。只有地图保存成功且几何轮廓合理，才算完成本阶段。

如果 Gazebo 中没有机器人，先检查仿真终端是否出现 `Spawn status: Successfully spawned entity`。若没有，检查 `ros2 service list | rg spawn_entity` 是否能看到 `/spawn_entity`，并确认 Gazebo server 没有提前退出。

RViz 报 `Frame [map] does not exist` 表示 SLAM 尚未发布 `map` 坐标系。确认仿真中的 `/scan`、`/odom` 有数据，且 `ros2 run tf2_ros tf2_echo odom base_footprint` 能持续输出后，再查看 `slam_toolbox` 终端是否报告等待 TF 或扫描数据。

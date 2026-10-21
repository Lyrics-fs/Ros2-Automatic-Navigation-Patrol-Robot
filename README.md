# ROS 2 移动机器人自主导航巡逻系统

本项目基于 ROS 2 Humble 和 Gazebo Classic，使用 TurtleBot3 Burger 搭建移动机器人自主导航与巡逻仿真，计划逐步完成 SLAM 建图、Nav2 定位与导航、巡逻点任务和 rosbag 实验复现。

机器人 URDF、Gazebo 模型及仿真世界来自官方 `turtlebot3_description` 和 `turtlebot3_gazebo` ROS 包。本仓库通过启动文件组合这些资源，不复制或维护上游模型副本。

## 当前进度

- 已选用 TurtleBot3 Burger 作为仿真底盘。
- `patrol_sim_bringup` 提供项目自己的模型显示和 Gazebo 仿真入口。
- 后续步骤：验证仿真话题与 TF，然后开展 SLAM 建图和 Nav2 导航。

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
export TURTLEBOT3_MODEL=burger
ros2 launch patrol_sim_bringup simulation.launch.py
```

该启动文件调用 TurtleBot3 官方 `turtlebot3_world.launch.py`，默认将机器人放置在 `x=-2.0, y=-0.5`。可以用 `x_pose` 和 `y_pose` 覆盖初始位置：

```bash
ros2 launch patrol_sim_bringup simulation.launch.py x_pose:=0.0 y_pose:=0.0
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

确认 `/scan`、`/odom`、`/clock` 和 `odom -> base_link` 正常后，再进入 SLAM 建图步骤。

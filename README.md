# ROS 2 移动机器人自主导航巡逻系统

本项目基于 ROS 2 Humble 和 Gazebo Classic，使用 TurtleBot3 Burger 搭建移动机器人自主导航与巡逻仿真，计划逐步完成 SLAM 建图、Nav2 定位与导航、巡逻点任务和 rosbag 实验复现。

机器人 URDF、Gazebo 模型及仿真世界来自官方 `turtlebot3_description` 和 `turtlebot3_gazebo` ROS 包。本仓库通过启动文件组合这些资源，不复制或维护上游模型副本。

## 当前进度

- 已选用 TurtleBot3 Burger 作为仿真底盘，并为仿真添加 RGB 相机。
- `patrol_sim_bringup` 提供项目自己的模型显示和 Gazebo 仿真入口。
- SLAM Toolbox 在线异步建图入口与 Burger 参数已加入。
- 已加入基于保存地图的 Nav2 启动入口，准备验证 AMCL 定位与目标点导航。
- 后续步骤：通过连续导航和动态障碍物测试调整 Nav2 参数，再实现巡逻点任务。

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

项目启动文件默认选择 Burger，并沿用官方世界、机器人模型和运动插件；启动时会给 Burger 添加 RGB 相机。机器人默认放置在 `x=-2.0, y=-0.5`。可以用 `model`、`x_pose` 和 `y_pose` 覆盖模型与初始位置：

```bash
ros2 launch patrol_sim_bringup simulation.launch.py model:=burger x_pose:=0.0 y_pose:=0.0
```

如需按原方式启动没有相机的 Burger，可以传入 `use_camera:=false`。其他 TurtleBot3 型号仍使用官方启动文件。

### RGB 相机验收

仿真启动终端出现“已生成带 RGB 相机的 Burger 机器人”后，在另一个终端检查图像、相机参数和 TF：

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 topic info /camera/image_raw
ros2 topic hz /camera/image_raw
ros2 topic echo /camera/camera_info --once
ros2 run tf2_ros tf2_echo base_link camera_optical_frame
```

图像应持续发布，分辨率为 640×480，目标频率约 15 Hz；`/camera/camera_info` 应包含相机内参，图像和相机参数的 `header.frame_id` 应为 `camera_optical_frame`。可在 RViz 中添加 **Image** 显示，话题选择 `/camera/image_raw` 检查画面。Gazebo 的相机画面可能受渲染负载影响，实际频率低于目标值时先确认图像是否持续更新。

若终端提示 `gzserver` 退出或等待 `/spawn_entity` 超时，先排查 Gazebo 启动问题；这时不会有相机话题。使用 ROS 2 时还需退出 Miniconda 的 `(base)` 环境，避免 ROS 脚本使用缺少系统依赖的 Conda Python。

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

## Nav2 定位与导航

先关闭 SLAM 建图和遥控节点，保留 Gazebo 仿真运行。新开终端启动 Nav2；默认使用本仓库保存的地图及 TurtleBot3 Humble Burger 参数：

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 launch patrol_sim_bringup navigation.launch.py
```

Nav2 启动后，项目会等待 AMCL 生命周期进入 active，再自动向 `/initialpose` 发布三次初始位姿。当前仿真固定出生点为 `x=-2.0, y=-0.5, yaw=0`，自动初始化默认使用这组地图坐标。地图文件本身不记录机器人出生位姿；如果修改 Gazebo 出生点或重新制作地图，需要确认机器人在地图中的实际坐标并同步调整初始位姿参数。AMCL 粒子云应收敛到机器人周围，TF 中应出现 `map -> odom -> base_footprint`。

如果地图中的初始位置与默认值不同，可覆盖地图坐标；朝向角使用弧度，例如朝向 90 度：

```bash
ros2 launch patrol_sim_bringup navigation.launch.py \
  initial_pose_x:=-2.0 initial_pose_y:=-0.5 initial_pose_yaw:=1.5708
```

需要手动校正时，可以关闭自动初始化，再在 RViz 中使用 **2D Pose Estimate**：

```bash
ros2 launch patrol_sim_bringup navigation.launch.py auto_initialize_pose:=false
```

定位稳定后使用 **Nav2 Goal** 在已知空闲区域设置目标。验收要求：规划路径出现在地图上，机器人沿路径移动并到达目标，期间 `/odom`、`/scan` 和 `/cmd_vel` 数据持续正常。无图形界面排查时可传入 `use_rviz:=false`。

如果需要使用另一份地图或调整 Nav2 参数，可以覆盖启动参数：

```bash
ros2 launch patrol_sim_bringup navigation.launch.py \
  map:=/绝对路径/其他地图.yaml \
  params_file:=/绝对路径/nav2参数.yaml
```

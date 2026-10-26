#!/usr/bin/python3

import sys
from pathlib import Path
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from gazebo_msgs.srv import SpawnEntity
import rclpy
from rclpy.node import Node


CAMERA_SENSOR = """
<sensor name="camera" type="camera">
  <pose>0.08 0 0.12 0 0 0</pose>
  <always_on>true</always_on>
  <update_rate>15</update_rate>
  <camera>
    <horizontal_fov>1.3962634</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.03</near>
      <far>30</far>
    </clip>
  </camera>
  <plugin name="robot_rgb_camera" filename="libgazebo_ros_camera.so">
    <camera_name>camera</camera_name>
    <frame_name>camera_optical_frame</frame_name>
  </plugin>
</sensor>
"""


def robot_sdf_with_camera(sdf_file):
    # 在任意包含 base_link 的模型上安装传感器，保留原有运动和雷达插件。
    sdf_path = Path(sdf_file)
    if not sdf_path.is_file():
        raise RuntimeError(f"机器人 SDF 文件不存在：{sdf_path}")
    sdf = ET.parse(sdf_path).getroot()
    base_link = sdf.find("./model/link[@name='base_link']")
    if base_link is None:
        raise RuntimeError("机器人 SDF 中未找到 base_link")
    base_link.append(ET.fromstring(CAMERA_SENSOR))
    return ET.tostring(sdf, encoding="unicode")


def main():
    rclpy.init()
    node = Node("spawn_robot_camera")
    try:
        node.declare_parameter("x_pose", -2.0)
        node.declare_parameter("y_pose", -0.5)
        node.declare_parameter("sdf_file", "")
        node.declare_parameter("entity_name", "burger")
        sdf_file = str(node.get_parameter("sdf_file").value)
        entity_name = str(node.get_parameter("entity_name").value)
        if not sdf_file:
            sdf_file = str(
                Path(get_package_share_directory("turtlebot3_gazebo"))
                / "models"
                / "turtlebot3_burger"
                / "model.sdf"
            )
        client = node.create_client(SpawnEntity, "/spawn_entity")
        if not client.wait_for_service(timeout_sec=30.0):
            node.get_logger().error("等待 /spawn_entity 超时，请检查 gzserver 是否正常运行")
            return 1

        request = SpawnEntity.Request()
        request.name = entity_name
        request.xml = robot_sdf_with_camera(sdf_file)
        request.initial_pose.position.x = float(node.get_parameter("x_pose").value)
        request.initial_pose.position.y = float(node.get_parameter("y_pose").value)
        request.initial_pose.position.z = 0.01
        request.initial_pose.orientation.w = 1.0

        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future, timeout_sec=30.0)
        if not future.done() or future.exception() is not None:
            node.get_logger().error("生成机器人超时或失败")
            return 1
        response = future.result()
        if not response.success:
            node.get_logger().error(f"生成机器人失败：{response.status_message}")
            return 1
        node.get_logger().info(f"已生成带 RGB 相机的机器人：{entity_name}")
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())

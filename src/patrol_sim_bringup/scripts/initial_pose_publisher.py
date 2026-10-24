#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import GetState
from rclpy.node import Node


class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__("initial_pose_publisher")
        self.declare_parameter("initial_pose_x", -2.0)
        self.declare_parameter("initial_pose_y", -0.5)
        self.declare_parameter("initial_pose_yaw", 0.0)

        self._publisher = self.create_publisher(
            PoseWithCovarianceStamped, "/initialpose", 10
        )
        self._state_client = self.create_client(GetState, "/amcl/get_state")
        self._pose = self._make_pose()

    def _make_pose(self):
        x = self.get_parameter("initial_pose_x").value
        y = self.get_parameter("initial_pose_y").value
        yaw = self.get_parameter("initial_pose_yaw").value

        pose = PoseWithCovarianceStamped()
        pose.header.frame_id = "map"
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y
        pose.pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.pose.orientation.w = math.cos(yaw / 2.0)
        pose.pose.covariance[0] = 0.25
        pose.pose.covariance[7] = 0.25
        pose.pose.covariance[35] = 0.0685
        return pose

    def initialize_when_ready(self):
        self.get_logger().info("等待 AMCL 激活后发送初始位姿")
        while rclpy.ok():
            if not self._state_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info("等待 /amcl/get_state 服务")
                continue

            request = GetState.Request()
            response = self._request_state(request)
            if response is None:
                continue
            if response.current_state.id == State.PRIMARY_STATE_ACTIVE:
                break
            self.get_logger().info(
                f"AMCL 当前状态为 {response.current_state.label}，等待激活"
            )

        if not rclpy.ok():
            return

        for attempt in range(3):
            self._pose.header.stamp = self.get_clock().now().to_msg()
            self._publisher.publish(self._pose)
            self.get_logger().info(
                f"已发布 map 初始位姿（第 {attempt + 1}/3 次）："
                f"x={self._pose.pose.pose.position.x:.2f}, "
                f"y={self._pose.pose.pose.position.y:.2f}"
            )
            if attempt < 2:
                rclpy.spin_once(self, timeout_sec=0.5)

    def _request_state(self, request):
        future = self._state_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
        if future.done() and future.exception() is None:
            return future.result()
        self.get_logger().warning("查询 AMCL 状态失败，将重试")
        return None


def main():
    rclpy.init()
    node = InitialPosePublisher()
    try:
        node.initialize_when_ready()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

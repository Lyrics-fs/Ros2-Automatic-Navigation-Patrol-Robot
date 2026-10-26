import json

from cv_bridge import CvBridge, CvBridgeError
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .backend import create_backend


class ModelDetector(Node):
    def __init__(self):
        super().__init__("model_detector")
        self.declare_parameter("backend", "yolo")
        self.declare_parameter("model_path", "models/yolo11n.pt")
        self.declare_parameter("model_options", "{}")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("annotated_topic", "/perception/image_annotated")
        self.declare_parameter("detections_topic", "/perception/detections")
        self.declare_parameter("confidence_threshold", 0.35)
        self.declare_parameter("image_size", 416)
        self.declare_parameter("inference_hz", 3.0)
        self.declare_parameter("device", "cpu")

        confidence = float(self.get_parameter("confidence_threshold").value)
        image_size = int(self.get_parameter("image_size").value)
        inference_hz = float(self.get_parameter("inference_hz").value)
        if not 0.0 < confidence <= 1.0:
            raise ValueError("confidence_threshold 必须大于 0 且不超过 1")
        if image_size <= 0 or inference_hz <= 0:
            raise ValueError("image_size 和 inference_hz 必须大于 0")

        try:
            options = json.loads(str(self.get_parameter("model_options").value))
        except json.JSONDecodeError as exc:
            raise ValueError(f"model_options 必须是有效 JSON：{exc}") from exc
        if not isinstance(options, dict):
            raise ValueError("model_options 必须是 JSON 对象")

        backend_name = str(self.get_parameter("backend").value)
        backend_config = {
            "model_path": str(self.get_parameter("model_path").value),
            "confidence_threshold": confidence,
            "image_size": image_size,
            "device": str(self.get_parameter("device").value),
            "options": options,
        }
        self.get_logger().info(f"初始化视觉后端：{backend_name}")
        self._backend = create_backend(backend_name, backend_config)
        self._bridge = CvBridge()
        self._latest_image = None

        image_topic = str(self.get_parameter("image_topic").value)
        annotated_topic = str(self.get_parameter("annotated_topic").value)
        detections_topic = str(self.get_parameter("detections_topic").value)
        self.create_subscription(
            Image, image_topic, self._remember_latest_image, qos_profile_sensor_data
        )
        self._annotated_publisher = self.create_publisher(Image, annotated_topic, 10)
        self._detections_publisher = self.create_publisher(String, detections_topic, 10)
        self.create_timer(1.0 / inference_hz, self._detect_latest_image)
        self.get_logger().info(
            f"订阅 {image_topic}，发布 {annotated_topic} 和 {detections_topic}"
        )

    def _remember_latest_image(self, image):
        # 推理慢于相机帧率时只保留最新画面，避免检测结果不断滞后。
        self._latest_image = image

    def _detect_latest_image(self):
        if self._latest_image is None:
            return
        image = self._latest_image
        self._latest_image = None

        try:
            frame = self._bridge.imgmsg_to_cv2(image, desired_encoding="bgr8")
            result = self._backend.infer(frame)
        except CvBridgeError as exc:
            self.get_logger().warning(f"相机图像转换失败：{exc}")
            return
        except Exception as exc:  # 模型运行时错误应被记录，不能让定时器静默退出。
            self.get_logger().error(f"视觉推理失败：{exc}")
            return

        annotated_frame = result.annotated_image if result.annotated_image is not None else frame
        annotated = self._bridge.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
        annotated.header = image.header
        self._annotated_publisher.publish(annotated)

        detections = [
            {
                "class_id": item.class_id,
                "class_name": item.class_name,
                "confidence": item.confidence,
                "bbox": {
                    "x_min": item.x_min,
                    "y_min": item.y_min,
                    "x_max": item.x_max,
                    "y_max": item.y_max,
                },
            }
            for item in result.detections
        ]
        payload = {
            "stamp": {
                "sec": image.header.stamp.sec,
                "nanosec": image.header.stamp.nanosec,
            },
            "frame_id": image.header.frame_id,
            "detections": detections,
        }
        self._detections_publisher.publish(
            String(data=json.dumps(payload, ensure_ascii=False))
        )


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ModelDetector()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

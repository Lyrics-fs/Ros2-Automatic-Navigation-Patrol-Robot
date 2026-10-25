import json

from cv_bridge import CvBridge, CvBridgeError
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String


class YoloDetector(Node):
    def __init__(self):
        super().__init__("yolo_detector")
        self.declare_parameter("weights", "yolo11n.pt")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("annotated_topic", "/perception/image_annotated")
        self.declare_parameter("detections_topic", "/perception/detections")
        self.declare_parameter("confidence_threshold", 0.35)
        self.declare_parameter("image_size", 416)
        self.declare_parameter("inference_hz", 3.0)
        self.declare_parameter("device", "cpu")

        self._confidence = float(self.get_parameter("confidence_threshold").value)
        self._image_size = int(self.get_parameter("image_size").value)
        self._inference_hz = float(self.get_parameter("inference_hz").value)
        self._device = str(self.get_parameter("device").value)
        if not 0.0 < self._confidence <= 1.0:
            raise ValueError("confidence_threshold 必须大于 0 且不超过 1")
        if self._image_size <= 0 or self._inference_hz <= 0:
            raise ValueError("image_size 和 inference_hz 必须大于 0")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("未安装 Ultralytics；请按 README 配置视觉虚拟环境") from exc

        weights = str(self.get_parameter("weights").value)
        self.get_logger().info(f"加载 YOLO 权重：{weights}")
        self._model = YOLO(weights)
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
        self.create_timer(1.0 / self._inference_hz, self._detect_latest_image)
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
        except CvBridgeError as exc:
            self.get_logger().warning(f"相机图像转换失败：{exc}")
            return

        result = self._model.predict(
            source=frame,
            imgsz=self._image_size,
            conf=self._confidence,
            device=self._device,
            verbose=False,
        )[0]

        # 保留原始图像时间戳，便于后续与里程计或地图数据对齐。
        annotated = self._bridge.cv2_to_imgmsg(result.plot(), encoding="bgr8")
        annotated.header = image.header
        self._annotated_publisher.publish(annotated)

        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
            detections.append(
                {
                    "class_id": class_id,
                    "class_name": result.names[class_id],
                    "confidence": float(box.conf.item()),
                    "bbox": {
                        "x_min": x_min,
                        "y_min": y_min,
                        "x_max": x_max,
                        "y_max": y_max,
                    },
                }
            )

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
        node = YoloDetector()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "weights",
                default_value="models/yolo11n.pt",
                description="YOLO11n 权重文件路径；首次使用时可自动下载到 models 目录。",
            ),
            DeclareLaunchArgument(
                "image_topic",
                default_value="/camera/image_raw",
                description="输入相机图像话题。",
            ),
            DeclareLaunchArgument(
                "annotated_topic",
                default_value="/perception/image_annotated",
                description="带检测框的输出图像话题。",
            ),
            DeclareLaunchArgument(
                "detections_topic",
                default_value="/perception/detections",
                description="JSON 格式的检测结果话题。",
            ),
            DeclareLaunchArgument(
                "confidence_threshold",
                default_value="0.35",
                description="目标检测置信度阈值，范围为 (0, 1]。",
            ),
            DeclareLaunchArgument(
                "image_size",
                default_value="416",
                description="YOLO 推理图像尺寸。",
            ),
            DeclareLaunchArgument(
                "inference_hz",
                default_value="3.0",
                description="目标推理频率，单位为 Hz。",
            ),
            DeclareLaunchArgument(
                "device",
                default_value="cpu",
                description="推理设备；先用 cpu 验证，可在确认 GPU 可用后调整。",
            ),
            Node(
                package="patrol_vision",
                executable="model_detector",
                name="yolo_detector",
                parameters=[
                    {
                        "backend": "yolo",
                        "model_path": LaunchConfiguration("weights"),
                        "model_options": "{}",
                        "image_topic": LaunchConfiguration("image_topic"),
                        "annotated_topic": LaunchConfiguration("annotated_topic"),
                        "detections_topic": LaunchConfiguration("detections_topic"),
                        "confidence_threshold": ParameterValue(
                            LaunchConfiguration("confidence_threshold"), value_type=float
                        ),
                        "image_size": ParameterValue(
                            LaunchConfiguration("image_size"), value_type=int
                        ),
                        "inference_hz": ParameterValue(
                            LaunchConfiguration("inference_hz"), value_type=float
                        ),
                        "device": LaunchConfiguration("device"),
                        "use_sim_time": True,
                    }
                ],
                output="screen",
            ),
        ]
    )

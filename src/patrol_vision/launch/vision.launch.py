from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("backend", default_value="yolo", description="视觉模型后端。"),
            DeclareLaunchArgument(
                "model_path", default_value="models/yolo11n.pt", description="模型权重或模型文件路径。"
            ),
            DeclareLaunchArgument(
                "model_options", default_value="{}", description="后端专属参数，使用 JSON 对象。"
            ),
            DeclareLaunchArgument("image_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument(
                "annotated_topic", default_value="/perception/image_annotated"
            ),
            DeclareLaunchArgument("detections_topic", default_value="/perception/detections"),
            DeclareLaunchArgument("confidence_threshold", default_value="0.35"),
            DeclareLaunchArgument("image_size", default_value="416"),
            DeclareLaunchArgument("inference_hz", default_value="3.0"),
            DeclareLaunchArgument("device", default_value="cpu"),
            Node(
                package="patrol_vision",
                executable="model_detector",
                name="model_detector",
                parameters=[
                    {
                        "backend": LaunchConfiguration("backend"),
                        "model_path": LaunchConfiguration("model_path"),
                        "model_options": LaunchConfiguration("model_options"),
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

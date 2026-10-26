"""视觉推理后端之间共享的数据结构。"""

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class Detection:
    """与具体模型无关的二维目标检测结果，坐标单位为像素。"""

    class_id: int
    class_name: str
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class InferenceResult:
    """单帧推理结果；标注图可为空，由 ROS 节点回退发布原图。"""

    detections: list[Detection]
    annotated_image: Optional[np.ndarray] = None


class VisionBackend:
    """模型适配器接口。新模型只需实现 infer 并返回统一结果。"""

    def infer(self, image: np.ndarray) -> InferenceResult:
        raise NotImplementedError


def create_backend(name: str, config: dict) -> VisionBackend:
    """按名称惰性加载后端，避免未使用的模型依赖影响 ROS 节点。"""

    if name == "yolo":
        from .yolo_backend import YoloBackend

        return YoloBackend(config)
    raise ValueError(f"未知视觉后端：{name}；当前支持：yolo")

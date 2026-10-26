"""Ultralytics YOLO 到项目统一视觉接口的适配器。"""

import logging

from .backend import Detection, InferenceResult, VisionBackend

_LOGGER = logging.getLogger(__name__)


class YoloBackend(VisionBackend):
    def __init__(self, config: dict):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("未安装 Ultralytics；请按 README 配置视觉虚拟环境") from exc

        weights = config["model_path"]
        self._confidence = config["confidence_threshold"]
        self._image_size = config["image_size"]
        self._device = config["device"]
        _LOGGER.info("加载 YOLO 权重：%s", weights)
        self._model = YOLO(weights)

    def infer(self, image):
        result = self._model.predict(
            source=image,
            imgsz=self._image_size,
            conf=self._confidence,
            device=self._device,
            verbose=False,
        )[0]

        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=str(result.names[class_id]),
                    confidence=float(box.conf.item()),
                    x_min=float(x_min),
                    y_min=float(y_min),
                    x_max=float(x_max),
                    y_max=float(y_max),
                )
            )

        return InferenceResult(detections=detections, annotated_image=result.plot())

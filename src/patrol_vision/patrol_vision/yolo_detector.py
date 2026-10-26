"""兼容旧入口；新功能统一由 model_detector 节点提供。"""

from .model_detector import main


if __name__ == "__main__":
    main()

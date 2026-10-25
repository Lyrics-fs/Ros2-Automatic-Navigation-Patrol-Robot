from glob import glob
import os

from setuptools import find_packages, setup


package_name = "patrol_vision"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Lyrics",
    maintainer_email="lyrics@example.com",
    description="基于 YOLO 的巡逻机器人图像目标检测节点。",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "yolo_detector = patrol_vision.yolo_detector:main",
        ],
    },
)

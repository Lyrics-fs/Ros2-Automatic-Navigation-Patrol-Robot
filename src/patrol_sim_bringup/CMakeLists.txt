cmake_minimum_required(VERSION 3.8)
project(patrol_sim_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch config rviz maps
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/initial_pose_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

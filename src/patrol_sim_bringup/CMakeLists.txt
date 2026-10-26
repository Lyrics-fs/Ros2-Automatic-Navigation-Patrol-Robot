cmake_minimum_required(VERSION 3.8)
project(patrol_sim_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY description launch config maps models rviz worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/initial_pose_publisher.py scripts/spawn_robot_camera.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

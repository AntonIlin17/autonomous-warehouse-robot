cmake_minimum_required(VERSION 3.8)
project(warehouse_robot_nav)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(nav_menu src/nav_menu.cpp)
ament_target_dependencies(nav_menu
  rclcpp
  rclcpp_action
  ament_index_cpp
  nav2_msgs
  geometry_msgs
)

install(TARGETS nav_menu
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY config launch maps params rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

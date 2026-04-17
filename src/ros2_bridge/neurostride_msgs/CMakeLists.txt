# CMakeLists.txt for neurostride_msgs package

cmake_minimum_required(VERSION 3.8)
project(neurostride_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 寻找依赖
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# 消息/服务/动作定义
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotState.msg"
  "msg/MotorCommand.msg"
  "msg/LocomotionCommand.msg"
  "msg/VLCommand.msg"
  "msg/PolicyAction.msg"
  "srv/GetPolicy.srv"
  "srv/SetVelocity.srv"
  DEPENDENCIES std_msgs geometry_msgs sensor_msgs
)

# 安装
ament_export_dependencies(rosidl_default_runtime)

ament_package()

# RobotState.msg
# 机器人状态消息

builtin_interfaces/Time stamp

float32 torso_height                  # 躯干高度 (m)
float64[4] torso_orientation          # 躯干姿态 (四元数 w, x, y, z)
float32[3] torso_velocity             # 躯干线速度 (m/s)
float32[3] torso_angular_velocity     # 躯干角速度 (rad/s)

float32[23] joint_positions           # 关节位置 (rad)
float32[23] joint_velocities          # 关节速度 (rad/s)
float32[23] joint_torques             # 关节扭矩 (N·m)

float32 left_foot_contact            # 左脚接触力 (N)
float32 right_foot_contact           # 右脚接触力 (N)

float32[3] velocity                  # 当前速度指令 (vx, vy, vyaw)
float32[23] action                   # 当前动作

bool is_stable                       # 是否稳定
float32 battery_level                # 电池电量 (0-1)

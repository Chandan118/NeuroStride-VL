# MotorCommand.msg
# 电机控制指令

builtin_interfaces/Time stamp

string[] joint_names                 # 关节名称列表
float32[] effort                    # 扭矩命令 (N·m)
float32[] position                  # 目标位置 (rad) [可选]
float32[] velocity                  # 目标速度 (rad/s) [可选]

uint8 mode                          # 控制模式
uint8 MODE_TORQUE = 0               # 扭矩控制
uint8 MODE_POSITION = 1             # 位置控制
uint8 MODE_VELOCITY = 2             # 速度控制

bool emergency_stop                 # 紧急停止

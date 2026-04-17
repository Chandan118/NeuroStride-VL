# LocomotionCommand.msg
# 运动控制命令

builtin_interfaces/Time stamp

float32 vx                          # X方向速度 (m/s)
float32 vy                          # Y方向速度 (m/s)
float32 vyaw                        # 角速度 (rad/s)

float32 step_height                 # 步高 (m)
float32 step_freq                   # 步频 (Hz)

bool enable                         # 使能/禁用

string gait_type                    # 步态类型: "walk", "trot", "run"

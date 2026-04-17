# PolicyAction.msg
# RL策略输出

builtin_interfaces/Time stamp

float32[] actions                   # 动作向量
float32 value                       # 价值估计
float32[23] logits                  # 策略logits（如果是离散动作）

uint32 step_count                   # 当前步数

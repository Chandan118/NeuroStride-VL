# PolicyAction.msg
# RL Policy Output

builtin_interfaces/Time stamp

float32[] actions                   # Action vector
float32 value                       # Value estimate
float32[23] logits                  # Policy logits (if discrete actions)

uint32 step_count                   # Current step count

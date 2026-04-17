# LocomotionCommand.msg
# Locomotion Control Command

builtin_interfaces/Time stamp

float32 vx                          # X velocity (m/s)
float32 vy                          # Y velocity (m/s)
float32 vyaw                        # Yaw rate (rad/s)

float32 step_height                 # Step height (m)
float32 step_freq                   # Step frequency (Hz)

bool enable                         # Enable/disable

string gait_type                    # Gait type: "walk", "trot", "run"

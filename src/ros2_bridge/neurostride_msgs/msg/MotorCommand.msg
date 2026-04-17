# MotorCommand.msg
# Motor Control Command

builtin_interfaces/Time stamp

string[] joint_names                 # Joint name list
float32[] effort                    # Torque command (N·m)
float32[] position                  # Target position (rad) [optional]
float32[] velocity                  # Target velocity (rad/s) [optional]

uint8 mode                          # Control mode
uint8 MODE_TORQUE = 0               # Torque control
uint8 MODE_POSITION = 1             # Position control
uint8 MODE_VELOCITY = 2             # Velocity control

bool emergency_stop                 # Emergency stop

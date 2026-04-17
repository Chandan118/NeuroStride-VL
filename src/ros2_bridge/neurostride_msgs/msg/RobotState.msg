# RobotState.msg
# Robot State Message

builtin_interfaces/Time stamp

float32 torso_height                  # Torso height (m)
float64[4] torso_orientation          # Torso orientation (quaternion w, x, y, z)
float32[3] torso_velocity             # Torso linear velocity (m/s)
float32[3] torso_angular_velocity     # Torso angular velocity (rad/s)

float32[23] joint_positions           # Joint positions (rad)
float32[23] joint_velocities          # Joint velocities (rad/s)
float32[23] joint_torques             # Joint torques (N·m)

float32 left_foot_contact            # Left foot contact force (N)
float32 right_foot_contact           # Right foot contact force (N)

float32[3] velocity                  # Current velocity command (vx, vy, vyaw)
float32[23] action                   # Current action

bool is_stable                       # Is stable
float32 battery_level                # Battery level (0-1)

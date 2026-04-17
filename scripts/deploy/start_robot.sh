#!/bin/bash
# NeuroStride-VL: Robot Startup Script (runs on Jetson Orin Nano)
# ============================================================
# Responsible for starting all necessary nodes and connecting hardware

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default parameters
USE_ROS2_CONTROL=false
MOTOR_PORT="/dev/ttyUSB0"
MODEL_PATH="models/trt/policy_fp16.engine"
CONFIG_FILE="configs/inference/deployment.yaml"

while [[ $# -gt 0 ]]; do
    case $1 in
        --ros2-control)
            USE_ROS2_CONTROL=true
            shift
            ;;
        --port)
            MOTOR_PORT="$2"
            shift 2
            ;;
        --model)
            MODEL_PATH="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            log_error "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL Robot Launcher"
log_info "=========================================="

# Check environment
log_info "Environment check..."

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not installed"
    exit 1
fi

# Check ROS2
if ! command -v ros2 &> /dev/null; then
    log_error "ROS2 not installed or not sourced"
    log_info "Please run: source /opt/ros/humble/setup.bash"
    exit 1
fi

# Check TensorRT engine
if [ ! -f "$MODEL_PATH" ]; then
    log_warn "TensorRT engine not found: $MODEL_PATH"
    log_info "Please run deployment script first:"
    log_info "  ./scripts/deploy/deploy_to_jetson.sh --host <ip>"
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "Activated virtual environment"
fi

# Build ROS2 packages if needed
log_info "Checking ROS2 packages..."
if [ ! -d "install/neurostride_msgs" ]; then
    log_info "Building ROS2 packages..."
    colcon build --symlink-install --packages-select neurostride_msgs neurostride_bridge
    source install/setup.bash
fi

# Start nodes
log_info "Starting robot nodes..."

# Use ROS2 launch (recommended)
# Create temporary launch file
LAUNCH_FILE="/tmp/neurostride_robot.launch.py"
cat > "$LAUNCH_FILE" << EOF
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='neurostride_bridge',
            executable='executor_node',
            name='executor',
            parameters=[
                {'model_path': '$MODEL_PATH'},
                {'use_ros2_control': $USE_ROS2_CONTROL},
                {'motor_port': '$MOTOR_PORT'},
                {'config_file': '$CONFIG_FILE'},
            ],
            output='screen',
        ),
    ])
EOF

# Start
ros2 launch "$LAUNCH_FILE" &

# Wait for node to start
sleep 3

# Check node status
if ros2 node list | grep -q "executor"; then
    log_success "✅ Executor node started"
else
    log_error "Node startup failed"
    exit 1
fi

# Display status info
log_info ""
log_info "=========================================="
log_info "  NeuroStride-VL Robot Running"
log_info "=========================================="
log_info ""
log_info "Monitoring commands:"
log_info "  List nodes:     ros2 node list"
log_info "  List topics:    ros2 topic list"
log_info "  View status:    ros2 topic echo /robot_state"
log_info "  Send velocity:  ros2 topic pub /cmd_vel geometry_msgs/Twist '{linear: {x: 0.5}, angular: {z: 0.0}}'"
log_info ""
log_info "Stop: Press Ctrl+C"
log_info ""

# Wait for interrupt
trap 'log_info "Stopping..."; kill $(pgrep -f "ros2 launch"); exit 0' INT
wait

#!/bin/bash
# NeuroStride-VL 机器人启动脚本（运行在 Jetson Orin Nano 上）
# ===========================================================
# 负责启动所有必要的节点并连接硬件

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色
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

# 默认参数
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
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL 机器人启动器"
log_info "=========================================="

# 检查环境
log_info "环境检查..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装"
    exit 1
fi

# 检查 ROS2
if ! command -v ros2 &> /dev/null; then
    log_error "ROS2 未安装或未 source"
    log_info "请运行: source /opt/ros/humble/setup.bash"
    exit 1
fi

# 检查 TensorRT 引擎
if [ ! -f "$MODEL_PATH" ]; then
    log_warn "TensorRT 引擎未找到: $MODEL_PATH"
    log_info "请先运行部署脚本:"
    log_info "  ./scripts/deploy/deploy_to_jetson.sh --host <ip>"
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "激活虚拟环境"
fi

# 编译 ROS2 包（如果需要）
log_info "检查 ROS2 包..."
if [ ! -d "install/neurostride_msgs" ]; then
    log_info "编译 ROS2 包..."
    colcon build --symlink-install --packages-select neurostride_msgs neurostride_bridge
    source install/setup.bash
fi

# 启动节点
log_info "启动机器人节点..."

# 使用 ROS2 launch 启动（推荐）
# 创建临时 launch 文件
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

# 启动
ros2 launch "$LAUNCH_FILE" &

# 等待节点启动
sleep 3

# 检查节点状态
if ros2 node list | grep -q "executor"; then
    log_success "✅ 执行器节点已启动"
else
    log_error "节点启动失败"
    exit 1
fi

# 显示状态信息
log_info ""
log_info "=========================================="
log_info "  NeuroStride-VL 机器人运行中"
log_info "=========================================="
log_info ""
log_info "监控命令:"
log_info "  查看节点:     ros2 node list"
log_info "  查看话题:     ros2 topic list"
log_info "  查看状态:     ros2 topic echo /robot_state"
log_info "  发送速度:     ros2 topic pub /cmd_vel geometry_msgs/Twist '{linear: {x: 0.5}, angular: {z: 0.0}}'"
log_info ""
log_info "停止: 按 Ctrl+C"
log_info ""

# 等待中断
trap 'log_info "正在停止..."; kill $(pgrep -f "ros2 launch"); exit 0' INT
wait

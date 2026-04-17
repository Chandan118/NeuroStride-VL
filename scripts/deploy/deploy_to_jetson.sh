#!/bin/bash
# NeuroStride-VL 部署到 Jetson Orin Nano
# ========================================
# 包含模型量化、传输、部署全流程

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
MODEL_PATH="models/checkpoints/sac_final.zip"
JETSON_HOST=""
JETSON_USER="jetson"
PRECISION="fp16"
SKIP_QUANTIZE=false
SKIP_TRANSFER=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL_PATH="$2"
            shift 2
            ;;
        --host)
            JETSON_HOST="$2"
            shift 2
            ;;
        --user)
            JETSON_USER="$2"
            shift 2
            ;;
        --precision)
            PRECISION="$2"
            shift 2
            ;;
        --skip-quantize)
            SKIP_QUANTIZE=true
            shift
            ;;
        --skip-transfer)
            SKIP_TRANSFER=true
            shift
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL Jetson 部署工具"
log_info "=========================================="

# 步骤 1: 量化模型（如果尚未量化）
if [ "$SKIP_QUANTIZE" = false ]; then
    log_info "步骤 1/3: 量化模型..."

    python3 src/utils/quantize.py \
        --input "$MODEL_PATH" \
        --output-dir models/trt \
        --model-type policy \
        --precision "$PRECISION" \
        --benchmark

    ENGINE_PATH="models/trt/policy_${PRECISION}.engine"

    if [ ! -f "$ENGINE_PATH" ]; then
        log_error "量化失败: $ENGINE_PATH 未生成"
        exit 1
    fi

    log_success "模型量化完成: $ENGINE_PATH"
else
    log_warn "跳过量化步骤"
    ENGINE_PATH="models/trt/policy_${PRECISION}.engine"
fi

# 步骤 2: 传输到 Jetson
if [ "$SKIP_TRANSFER" = false ]; then
    if [ -z "$JETSON_HOST" ]; then
        log_error "未指定 Jetson 主机地址 (--host)"
        log_info "用法: $0 --host <jetson-ip> --user <username>"
        exit 1
    fi

    log_info "步骤 2/3: 传输文件到 Jetson ($JETSON_USER@$JETSON_HOST)..."

    # 创建远程目录
    ssh "$JETSON_USER@$JETSON_HOST" "mkdir -p ~/neurostride-vl/models/trt"

    # 传输量化后的模型
    scp "$ENGINE_PATH" "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/models/trt/"

    # 传输部署脚本
    scp scripts/deploy/start_robot.sh "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/scripts/"
    ssh "$JETSON_USER@$JETSON_HOST" "chmod +x ~/neurostride-vl/scripts/start_robot.sh"

    # 传输 ROS2 包
    scp -r src/ros2_bridge "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/src/"

    log_success "文件传输完成"
else
    log_warn "跳过文件传输"
fi

# 步骤 3: 在 Jetson 上编译和启动
if [ -n "$JETSON_HOST" ]; then
    log_info "步骤 3/3: 在 Jetson 上编译 ROS2 包并启动..."

    ssh "$JETSON_USER@$JETSON_HOST" bash << 'EOF'
        cd ~/neurostride-vl

        # 激活环境
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi

        # 编译 ROS2 包
        log_info "编译 ROS2 包..."
        colcon build --symlink-install --packages-select neurostride_msgs neurostride_bridge

        # 源 setup
        source install/setup.bash

        # 启动执行器节点
        log_info "启动执行器节点..."
        ros2 run neurostride_bridge executor_node
EOF

    log_success "Jetson 部署完成！"
fi

log_info ""
log_info "=========================================="
log_info "  部署完成"
log_info "=========================================="
log_info "下一步:"
log_info "1. 在 Mac M2 Pro 上启动指挥官节点:"
log_info "   ros2 run neurostride_bridge commander_node"
log_info ""
log_info "2. 验证通信:"
log_info "   ros2 topic echo /cmd_vel"
log_info "   ros2 topic echo /robot_state"
log_info ""

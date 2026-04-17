#!/bin/bash
# NeuroStride-VL 训练启动脚本
# ================================
# 用于启动强化学习训练

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

# 解析命令行参数
ALGO="sac"
ENV="unitree_g1"
TIMESTEPS=1000000
CONFIG=""
DEVICE="auto"
VERBOSE=1

while [[ $# -gt 0 ]]; do
    case $1 in
        --algo)
            ALGO="$2"
            shift 2
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --timesteps)
            TIMESTEPS="$2"
            shift 2
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --quiet)
            VERBOSE=0
            shift
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL 训练启动器"
log_info "=========================================="
log_info "算法: $ALGO"
log_info "环境: $ENV"
log_info "训练步数: $TIMESTEPS"
log_info "设备: $DEVICE"

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "激活虚拟环境: venv"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    log_info "激活虚拟环境: .venv"
elif command -v conda &> /dev/null && [[ "$CONDA_DEFAULT_ENV" == "neurostride" ]]; then
    log_info "使用 Conda 环境: neurostride"
else
    log_warn "未检测到虚拟环境，使用系统 Python"
fi

# 构建 Python 命令
CMD="python3 src/agents/rl_agent.py"

if [ "$VERBOSE" -eq 1 ]; then
    CMD="$CMD --verbose 1"
fi

# 执行训练
log_info "开始训练..."
echo ""

python3 -m neurostride.agents.train \
    --algo "$ALGO" \
    --env-name "$ENV" \
    --total-timesteps "$TIMESTEPS" \
    --device "$DEVICE" \
    ${CONFIG:+--config "$CONFIG"}

echo ""
log_info "训练完成！"
log_info "模型保存在: models/checkpoints/"
log_info "日志在: logs/"

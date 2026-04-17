#!/bin/bash
# NeuroStride-VL: Training Launcher Script
# ==========================================
# Used to start reinforcement learning training

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

# Parse command line arguments
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
            log_error "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL Training Launcher"
log_info "=========================================="
log_info "Algorithm: $ALGO"
log_info "Environment: $ENV"
log_info "Timesteps: $TIMESTEPS"
log_info "Device: $DEVICE"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "Activated virtual environment: venv"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    log_info "Activated virtual environment: .venv"
elif command -v conda &> /dev/null && [[ "$CONDA_DEFAULT_ENV" == "neurostride" ]]; then
    log_info "Using Conda environment: neurostride"
else
    log_warn "No virtual environment detected, using system Python"
fi

# Build Python command
CMD="python3 src/agents/rl_agent.py"

if [ "$VERBOSE" -eq 1 ]; then
    CMD="$CMD --verbose 1"
fi

# Execute training
log_info "Starting training..."
echo ""

python3 -m neurostride.agents.train \
    --algo "$ALGO" \
    --env-name "$ENV" \
    --total-timesteps "$TIMESTEPS" \
    --device "$DEVICE" \
    ${CONFIG:+--config "$CONFIG"}

echo ""
log_info "Training complete!"
log_info "Models saved to: models/checkpoints/"
log_info "Logs in: logs/"

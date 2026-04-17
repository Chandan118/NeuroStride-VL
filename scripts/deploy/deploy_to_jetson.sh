#!/bin/bash
# NeuroStride-VL: Deploy to Jetson Orin Nano
# ============================================
# Full pipeline: model quantization, transfer, and deployment

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
MODEL_PATH="models/checkpoints/sac_final.zip"
JETSON_HOST=""
JETSON_USER="jetson"
PRECISION="fp16"
SKIP_QUANTIZE=false
SKIP_TRANSFER=false

# Parse arguments
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
            log_error "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

log_info "=========================================="
log_info "  NeuroStride-VL Jetson Deployment Tool"
log_info "=========================================="

# Step 1: Quantize model (if not already quantized)
if [ "$SKIP_QUANTIZE" = false ]; then
    log_info "Step 1/3: Quantizing model..."

    python3 src/utils/quantize.py \
        --input "$MODEL_PATH" \
        --output-dir models/trt \
        --model-type policy \
        --precision "$PRECISION" \
        --benchmark

    ENGINE_PATH="models/trt/policy_${PRECISION}.engine"

    if [ ! -f "$ENGINE_PATH" ]; then
        log_error "Quantization failed: $ENGINE_PATH not generated"
        exit 1
    fi

    log_success "Model quantization complete: $ENGINE_PATH"
else
    log_warn "Skipping quantization step"
    ENGINE_PATH="models/trt/policy_${PRECISION}.engine"
fi

# Step 2: Transfer to Jetson
if [ "$SKIP_TRANSFER" = false ]; then
    if [ -z "$JETSON_HOST" ]; then
        log_error "Jetson host address not specified (--host)"
        log_info "Usage: $0 --host <jetson-ip> --user <username>"
        exit 1
    fi

    log_info "Step 2/3: Transferring files to Jetson ($JETSON_USER@$JETSON_HOST)..."

    # Create remote directory
    ssh "$JETSON_USER@$JETSON_HOST" "mkdir -p ~/neurostride-vl/models/trt"

    # Transfer quantized model
    scp "$ENGINE_PATH" "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/models/trt/"

    # Transfer deployment script
    scp scripts/deploy/start_robot.sh "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/scripts/"
    ssh "$JETSON_USER@$JETSON_HOST" "chmod +x ~/neurostride-vl/scripts/start_robot.sh"

    # Transfer ROS2 packages
    scp -r src/ros2_bridge "$JETSON_USER@$JETSON_HOST:~/neurostride-vl/src/"

    log_success "File transfer complete"
else
    log_warn "Skipping file transfer"
fi

# Step 3: Build and start on Jetson
if [ -n "$JETSON_HOST" ]; then
    log_info "Step 3/3: Building ROS2 packages and starting on Jetson..."

    ssh "$JETSON_USER@$JETSON_HOST" bash << 'EOF'
        cd ~/neurostride-vl

        # Activate environment if exists
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi

        # Build ROS2 packages
        log_info "Building ROS2 packages..."
        colcon build --symlink-install --packages-select neurostride_msgs neurostride_bridge

        # Source setup
        source install/setup.bash

        # Start executor node
        log_info "Starting executor node..."
        ros2 run neurostride_bridge executor_node
EOF

    log_success "Jetson deployment complete!"
fi

log_info ""
log_info "=========================================="
log_info "  Deployment Complete"
log_info "=========================================="
log_info "Next steps:"
log_info "1. Start commander node on Mac M2 Pro:"
log_info "   ros2 run neurostride_bridge commander_node"
log_info ""
log_info "2. Verify communication:"
log_info "   ros2 topic echo /cmd_vel"
log_info "   ros2 topic echo /robot_state"
log_info ""

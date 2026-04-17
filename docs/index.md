# NeuroStride-VL Documentation

Welcome to **NeuroStride-VL** documentation!

NeuroStride-VL is an end-to-end bipedal robot control framework combining LLM high-level reasoning with deep reinforcement learning for real-time balance control.

## 🚀 Quick Navigation

- **Installation** → Set up on Mac M2 Pro or Jetson Orin Nano
- **Tutorials** → Step-by-step guides
- **API Reference** → Complete Python API
- **Architecture** → System design overview
- **Training** → RL locomotion training
- **Deployment** → Edge deployment & optimization

## 📖 Getting Started

### Prerequisites

- Python 3.10+
- MuJoCo 2.3+ (free license for academics)
- PyTorch 2.0+
- 16GB RAM (32GB recommended)

### One-Line Install

```bash
git clone https://github.com/Chandan118/NeuroStride-VL.git
cd NeuroStride-VL
chmod +x scripts/install/setup.sh
./scripts/install/setup.sh
```

### Verify

```bash
python3 -c "import neurostride; print('✅ Installed!')"
```

## 📊 Project Highlights

- 🧠 **Vision-Language Control** - Natural language commands via Qwen-VL
- 🦾 **RL Locomotion** - PPO/SAC for robust walking policies
- 🔄 **Distributed Architecture** - Mac M2 Pro (commander) + Jetson Orin Nano (executor)
- ⚡ **Real-Time Performance** - 500Hz control, 2.8ms inference (INT8)
- 🚀 **Sim2Real Transfer** - Train in MuJoCo, deploy on real robots

## 🎯 Quick Example

Train a walking policy:

```bash
python3 src/train/train_locomotion.py \
    --robot unitree_g1 \
    --algo ppo \
    --timesteps 1_000_000 \
    --save-path models/checkpoints/
```

Deploy to Jetson:

```bash
python3 src/utils/quantize.py \
    --input models/checkpoints/sac_policy.pt \
    --output models/trt/sac_policy.engine \
    --precision int8

./scripts/deploy/deploy_to_jetson.sh \
    --model models/trt/sac_policy.engine \
    --robot /dev/ttyUSB0
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Training time (1M steps) | 6.5-8.2 hours |
| Inference latency (INT8) | 2.8ms |
| Control frequency | 500 Hz |
| Real-time capability | ✅ Yes |

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](https://github.com/Chandan118/NeuroStride-VL/blob/main/CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](https://github.com/Chandan118/NeuroStride-VL/blob/main/LICENSE) file.

---

**Made with ❤️ by the NeuroStride-VL Team**

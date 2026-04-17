# NeuroStride-VL Documentation

Welcome to **NeuroStride-VL** documentation! This is an end-to-end bipedal robot control framework combining LLM reasoning with deep reinforcement learning.

## 📖 Quick Links

- [Installation Guide](installation/) - Set up NeuroStride-VL on Mac M2 Pro or Jetson Orin Nano
- [Tutorials](tutorials/) - Step-by-step guides for common tasks
- [API Reference](api/) - Complete Python API documentation
- [Architecture](architecture/) - System design and component overview
- [Training Guide](training/) - Train walking policies with RL
- [Deployment](deployment/) - Edge deployment and optimization
- [Advanced Topics](advanced/) - Custom robots and reward functions

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MuJoCo 2.3+
- PyTorch 2.0+
- ROS2 Humble (optional, for distributed deployment)

### Quick Installation

```bash
git clone https://github.com/Chandan118/NeuroStride-VL.git
cd NeuroStride-VL
chmod +x scripts/install/setup.sh
./scripts/install/setup.sh
```

### Verify Installation

```bash
python3 -c "import neurostride; print('✅ NeuroStride-VL installed!')"
python3 tests/unit/test_installation.py
```

## 📊 Project Overview

NeuroStride-VL combines three cutting-edge technologies:

1. **🧠 Vision-Language Understanding** - Qwen-2-VL for scene analysis
2. **🦾 Deep Reinforcement Learning** - PPO/SAC for walking policies
3. **🔄 Distributed Architecture** - Mac M2 Pro + Jetson Orin Nano + ROS2

```mermaid
graph TB
    subgraph "Mac M2 Pro"
        A[Qwen-2-VL] --> B[Commands]
    end
    subgraph "ROS2"
        B --> C[Topics/Services]
    end
    subgraph "Jetson Orin Nano"
        C --> D[SAC Policy]
        D --> E[Motors]
    end
```

## 🎯 Key Features

- ✅ **Natural Language Control** - Tell robot what to do in plain English
- ✅ **End-to-End Learning** - From perception to control in one pipeline
- ✅ **Real-Time Performance** - 500Hz control on Jetson Orin Nano
- ✅ **Sim2Real Transfer** - Train in simulation, deploy on real hardware
- ✅ **Modular Design** - Easy to extend with new robots and tasks

## 📈 Performance

| Metric | Value |
|--------|-------|
| Training time (1M steps) | 6.5-8.2 hours |
| Inference latency (INT8) | 2.8ms |
| Control frequency | 500 Hz |
| Real-time capability | ✅ Yes |

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](../CONTRIBUTING.md) and submit pull requests.

## 📄 License

MIT License - see [LICENSE](../LICENSE) file.

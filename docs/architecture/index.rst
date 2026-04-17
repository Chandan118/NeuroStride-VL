.. _architecture-overview:

====================
System Architecture
====================

Deep dive into NeuroStride-VL's architecture and design decisions.

.. toctree::
   :maxdepth: 2
   :caption: Architecture Sections:

   overview
   components
   dataflow
   ros2_integration

====================
Architecture Overview
====================

NeuroStride-VL follows a **distributed, multi-modal** architecture combining vision-language understanding with reinforcement learning for robotic control.

High-Level Design
==================

.. mermaid:: ../../../src/architecture/system_architecture.mermaid
   :alt: System Architecture

Core Design Principles
======================

1. **Separation of Concerns**
   - Perception (Mac M2 Pro) separate from control (Jetson Orin Nano)
   - High-level reasoning on powerful hardware
   - Real-time control on embedded hardware

2. **Latency Budget Compliance**
   - Total control loop: <5ms (real-time)
   - Policy inference: <3ms (INT8 quantized)
   - ROS2 communication: <1ms

3. **Modularity**
   - Each component can be swapped independently
   - Easy to add new robots, algorithms, sensors

4. **Sim2Real Transfer**
   - Train entirely in simulation (MuJoCo)
   - Deploy directly to hardware with minimal adaptation

System Components
==================

Hardware Architecture
----------------------

.. mermaid:: ../../../src/architecture/hardware_architecture.mermaid
   :alt: Hardware Architecture

Software Stack
---------------

.. mermaid:: ../../../src/architecture/software_stack.mermaid
   :alt: Software Stack

Data Flow
==========

1. **Perception Layer**
   - Camera captures RGB image (640x480 @ 30Hz)
   - IMU provides orientation/acceleration (1kHz)
   - Qwen-VL processes image + optional text command
   - Output: high-level navigation command

2. **Planning Layer**
   - Converts natural language to motion goals
   - Plans path using environment map
   - Generates target velocity commands

3. **Control Layer**
   - SAC policy receives state observation (377-dim)
   - Computes joint torques (12 DoF for Unitree G1)
   - Sends commands to motor drivers @ 500Hz

4. **Feedback Loop**
   - Robot state fed back to MuJoCo simulation
   - Simulation computes reward for RL training
   - Policy updated via PPO/SAC

Performance Characteristics
============================

| Layer | Latency | Hardware | Frequency |
|-------|---------|----------|-----------|
| Perception | 320ms (INT8) | Mac M2 Pro | 3Hz |
| Planning | <1ms | Mac M2 Pro | 30Hz |
| Control | 2.8ms | Jetson Orin Nano | 500Hz |
| Total | ~325ms | - | 3Hz |

Trade-offs
===========

- **Accuracy vs Speed**: FP32 (accurate) vs INT8 (fast)
- **Complexity vs Real-time**: Larger models need quantization
- **Sim vs Real**: Simulation enables safe training, requires domain randomization

Security Considerations
========================

- ROS2 communication can be encrypted
- All models signed to prevent tampering
- Watchdog timers for fail-safe behavior

Next Steps
==========

- :doc:`components` - Deep dive into each component
- :doc:`dataflow` - Detailed data pipeline analysis
- :doc:`ros2_integration` - ROS2 communication details

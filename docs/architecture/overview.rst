.. _architecture-overview-detailed:

====================
System Architecture Overview
====================

Comprehensive view of NeuroStride-VL's architecture.

System Diagram
===============

.. mermaid:: ../../../src/architecture/full_system.mermaid
   :alt: Full System Architecture

Component Breakdown
=====================

The system consists of 5 major layers:

1. **Perception Layer**
   - Camera (RGB @ 30fps)
   - IMU (1000Hz orientation/acceleration)
   - Qwen-VL model (2B parameters)

2. **Planning Layer**
   - Command parser (text → velocity)
   - Path planner (obstacle avoidance)
   - Behavior tree (task sequencing)

3. **Control Layer**
   - Policy network (377 → 12)
   - MPC (Model Predictive Control) fallback
   - Safety filter (joint limits)

4. **Hardware Interface**
   - ROS2 topics (/cmd_vel, /joint_torques)
   - Serial/USB (motor drivers)
   - Real-time kernel (Jetson)

5. **Simulation & Training**
   - MuJoCo physics (1000Hz)
   - Experience replay buffer
   - PPO/SAC trainer

Data Flow Architecture
========================

.. mermaid:: ../../../src/architecture/data_flow.mermaid
   :alt: Data Flow

Communication Protocols
=========================

Mac M2 Pro → Jetson Orin Nano:
- ROS2 DDS (Data Distribution Service)
- QoS: Reliability = RELIABLE, Durability = TRANSIENT_LOCAL
- Latency target: <10ms

Jetson → Motors:
- Serial UART @ 500Hz
- Protocol: Unitree SDK
- Command: 12× float32 (torques)

Security & Safety
===================

- Watchdog timer resets if no command in 100ms
- Torque limits enforced in hardware
- Emergency stop via ROS2 service
- All models cryptographically signed

Fault Tolerance
================

- Graceful degradation (switch to open-loop)
- Auto-reconnect on ROS2 failure
- Health monitoring (CPU, GPU, temperature)
- Crash recovery (save state periodically)

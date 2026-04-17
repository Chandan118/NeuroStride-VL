.. _deployment-guide:

===========
Deployment Guide
===========

Deploy NeuroStride-VL on edge devices and production systems.

.. toctree::
   :maxdepth: 2
   :caption: Deployment Options:

   edge
   quantization
   ros2_deployment
   monitoring

====================
Edge Deployment
====================

Deploy trained policies to Jetson Orin Nano for real-time control.

Hardware Requirements
=======================

**Minimum:**
- Jetson Orin Nano Developer Kit
- 32GB eMMC storage
- 8GB RAM (4GB may work with INT8 models)

**Recommended:**
- Jetson Orin NX (better performance)
- 64GB NVMe SSD
- Active cooling ( Jetson fan)

Software Stack
===============

Jetson must have:

- JetPack 6.0+ (Ubuntu 22.04, CUDA 11.8, TensorRT 8.6)
- ROS2 Humble (optional, for ROS2 bridge)
- Python 3.8+

See :doc:`/installation/jetson_orin_nano` for full setup.

Deployment Steps
=================

1. **Export model** from training machine:

   .. code-block:: bash

      # Convert PyTorch to ONNX
      python3 src/utils/export_onnx.py \
          --input models/checkpoints/sac_policy.pt \
          --output models/onnx/sac_policy.onnx

      # Convert ONNX to TensorRT (run on Jetson)
      python3 src/utils/trt_converter.py \
          --input models/onnx/sac_policy.onnx \
          --output models/trt/sac_policy.engine \
          --precision fp16  # or int8

2. **Transfer to Jetson**:

   .. code-block:: bash

      scp -r models/trt jetson@192.168.1.100:~/NeuroStride-VL/models/

3. **Run deployment script**:

   .. code-block:: bash

      ./scripts/deploy/deploy_to_jetson.sh \
          --model models/trt/sac_policy.engine \
          --robot /dev/ttyUSB0

4. **Start robot**:

   .. code-block:: bash

      ./scripts/deploy/start_robot.sh

Performance Expectations
==========================

| Model | Precision | Latency | FPS |
|-------|-----------|---------|-----|
| SAC Policy | FP32 | 12.4ms | 80 |
| SAC Policy | FP16 | 4.1ms | 240 |
| SAC Policy | INT8 | 2.8ms | 350 |

For 500Hz control (2ms per cycle), **INT8 is required**.

Troubleshooting Deployment
===========================

Model Fails to Load
---------------------

Check TensorRT version compatibility:

.. code-block:: bash

   python3 -c "import tensorrt as trt; print(trt.__version__)"

TensorRT engine must be built on target Jetson (not cross-compiled).

Motor Not Responding
=====================

Verify serial connection:

.. code-block:: bash

   ls -l /dev/ttyUSB*
   sudo chmod 666 /dev/ttyUSB0

Check motor power and USB-C connection.

High Latency
=============

Ensure TensorRT engine is INT8 quantized. Check:

.. code-block:: python

   from neurostride.utils import profile_model
   profile_model("models/trt/sac_policy.engine")

Next Steps
==========

- Optimize with :doc:`quantization`
- Set up :doc:`monitoring`
- Configure :doc:`ros2_deployment`

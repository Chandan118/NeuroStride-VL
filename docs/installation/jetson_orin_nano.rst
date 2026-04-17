.. _jetson-orin-nano-installation:

==========================
Jetson Orin Nano Installation
==========================

This guide covers installing NeuroStride-VL on NVIDIA Jetson Orin Nano for edge deployment.

System Requirements
-------------------

- **Hardware**: Jetson Orin Nano Developer Kit
- **OS**: Ubuntu 22.04 (JetPack 6.0+)
- **Storage**: 32GB minimum (64GB recommended)
- **Power**: Adequate power supply required for training

Step 1: Flash JetPack
----------------------

Download and flash **JetPack 6.0** or later from NVIDIA's website. This includes:

- Ubuntu 22.04
- CUDA 11.8
- cuDNN 8.9
- TensorRT 8.6
- ROS2 Humble (optional)

Step 2: System Update
-----------------------

.. code-block:: bash

   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-dev libopenblas-dev libomp-dev

Step 3: Install ROS2 (Optional)
---------------------------------

For full distributed deployment:

.. code-block:: bash

   sudo apt install ros-humble-desktop  # Full desktop version
   # Or minimal:
   # sudo apt install ros-humble-ros-base

Source ROS2 in your ``.bashrc``:

.. code-block:: bash

   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc

Step 4: Install TensorRT
--------------------------

.. code-block:: bash

   sudo apt install python3-libnvinfer-dev libnvinfer-dev

Step 5: Install PyTorch for Jetson
------------------------------------

Jetson requires optimized PyTorch builds:

.. code-block:: bash

   wget https://nvidia-ai-iot.github.io/torch2trt/install_torch.sh
   sudo bash install_torch.sh

Verify CUDA is available:

.. code-block:: bash

   python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

Expected output: ``CUDA available: True``

Step 6: Clone and Install NeuroStride-VL
------------------------------------------

.. code-block:: bash

   cd ~
   git clone https://github.com/Chandan118/NeuroStride-VL.git
   cd NeuroStride-VL

   # Install Python dependencies
   pip3 install -r requirements.txt --no-cache-dir

   # Build ROS2 packages (if ROS2 installed)
   colcon build --symlink-install
   source install/setup.bash

Step 7: Verify Installation
-----------------------------

.. code-block:: bash

   python3 tests/unit/test_installation.py

Troubleshooting
===============

CUDA/TensorRT Issues
---------------------

If TensorRT installation fails:

.. code-block:: bash

   sudo apt update
   sudo apt install --reinstall python3-libnvinfer-dev libnvinfer-dev

Verify TensorRT:

.. code-block:: bash

   python3 -c "import tensorrt as trt; print(f'TensorRT version: {trt.__version__}')"

Out of Memory
-------------

Jetson Orin Nano has limited RAM (8GB). Recommendations:

1. Use smaller batch sizes
2. Enable model quantization (INT8)
3. Close unnecessary applications
4. Use swap space if needed

ROS2 Build Failures
--------------------

If ``colcon build`` fails:

.. code-block:: bash

   # Install missing dependencies
   sudo apt install ros-humble-ament-cmake
   sudo apt install ros-humble-rosidl-default-generators

   # Clean and rebuild
   rm -rf build/ install/ log/
   colcon build --symlink-install

Performance Optimization
========================

To maximize performance on Jetson:

1. **Use TensorRT**: Convert PyTorch models to TensorRT engines
2. **Quantize to INT8**: 4x speedup with minimal accuracy loss
3. **Set Jetson to MAXN mode**: ``sudo nvpmodel -m 0``
4. **Increase clock frequency**: ``sudo jetson_clocks``

Next Steps
==========

- Try :doc:`deployment guide <../deployment/edge>`
- Run :doc:`demo examples <../tutorials/quick_start>`
- Learn about :doc:`optimization techniques <../advanced/optimization>`

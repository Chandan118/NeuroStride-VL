.. _installation-index:

====================
Installation Guide
====================

This guide covers installing NeuroStride-VL on different platforms.

.. toctree::
   :maxdepth: 2
   :caption: Installation Sections:

   mac_m2_pro
   jetson_orin_nano
   docker
   from_source

====================
Quick Start
====================

Prerequisites
-------------

- **Python**: 3.10 or higher
- **MuJoCo**: 2.3+ (free license available for academics)
- **PyTorch**: 2.0+
- **ROS2 Humble**: Optional (for distributed deployment)

One-Line Installation
---------------------

The fastest way to get started:

.. code-block:: bash

   git clone https://github.com/Chandan118/NeuroStride-VL.git
   cd NeuroStride-VL
   chmod +x scripts/install/setup.sh
   ./scripts/install/setup.sh

The setup script will:
- Detect your OS (macOS/Linux)
- Install all Python dependencies
- Configure MuJoCo license
- Download pre-trained models (optional)
- Set up ROS2 environment (Linux only)

Verification
------------

After installation:

.. code-block:: bash

   python3 -c "import neurostride; print('✅ NeuroStride-VL installed!')"
   python3 tests/unit/test_installation.py

Expected output:

.. code-block:: bash

   ✅ All imports successful!
   ✅ MuJoCo initialized
   ✅ PyTorch CUDA/MPS available
   ✅ Installation complete!

Platform-Specific Guides
========================

Select your platform for detailed instructions:

- :ref:`Mac M2 Pro <mac-m2-pro-installation>`
- :ref:`Jetson Orin Nano <jetson-orin-nano-installation>`
- :ref:`Docker <docker-installation>`
- :ref:`From Source <from-source-installation>`

.. _mac-m2-pro-installation:

====================
Mac M2 Pro Installation
====================

This guide covers installing NeuroStride-VL on Apple Silicon Macs (M1/M2/M3).

System Requirements
-------------------

- **OS**: macOS 12.5+ (Monterey or later)
- **CPU**: Apple Silicon (M1/M2/M3 series)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 20GB free space

Step 1: Install Miniforge
--------------------------

Miniforge provides native ARM64 Python on macOS:

.. code-block:: bash

   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
   bash Miniforge3-MacOSX-arm64.sh

Follow the prompts. Restart your terminal after installation.

Step 2: Create Virtual Environment
------------------------------------

.. code-block:: bash

   conda create -n neurostride python=3.10
   conda activate neurostride

Step 3: Install PyTorch (MPS Backend)
---------------------------------------

Use Apple Silicon-optimized PyTorch:

.. code-block:: bash

   conda install pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

Verify MPS (Metal Performance Shaders) is available:

.. code-block:: bash

   python3 -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"

Expected output: ``MPS available: True``

Step 4: Install MuJoCo
-----------------------

Easiest method via conda:

.. code-block:: bash

   conda install -c conda-forge mujoco

Alternatively, download from `mujoco.org <https://mujoco.org/download/>`_ and place the ``mujoco210`` folder in ``~/.mujoco/``.

Step 5: Install Project Dependencies
--------------------------------------

.. code-block:: bash

   pip install -r requirements.txt

Step 6: Verify Installation
-----------------------------

.. code-block:: bash

   python3 tests/unit/test_installation.py

Troubleshooting
===============

ROS2 on macOS
--------------

ROS2 does not support macOS natively. Options:

1. **Docker** (recommended):
   .. code-block:: bash

      docker run -it --rm --net=host osrf/ros:humble-desktop

2. **Run ROS2 on Jetson**: Develop on Mac, deploy and test on Jetson hardware.

MuJoCo License Error
---------------------

If you see license errors:

1. Get a free academic license from `mujoco.org <https://mujoco.org/>`_
2. Place the key at ``~/.mujoco/mjkey.txt``

MPS Backend Issues
-------------------

If MPS is not available:

1. Update to macOS 12.5+
2. Update PyTorch: ``pip install --upgrade torch``
3. Verify with: ``python3 -c "import torch; print(torch.__version__)"``

Next Steps
==========

- Run the :doc:`quick start guide <../tutorials/quick_start>`
- Try :doc:`training examples <../training/basics>`
- Explore :doc:`architecture documentation <../architecture/overview>`

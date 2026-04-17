.. _quick-start-tutorial:

==========
Quick Start
==========

Get NeuroStride-VL up and running in **5 minutes**!

What You'll Learn
=================

✅ Train a bipedal robot to walk  
✅ Run vision-language commands  
✅ Deploy to edge devices

Prerequisites
=============

- Python 3.10+ installed
- MuJoCo license (free for academics)
- Git

Step 1: Clone and Install (2 min)
===================================

.. code-block:: bash

   git clone https://github.com/Chandan118/NeuroStride-VL.git
   cd NeuroStride-VL
   chmod +x scripts/install/setup.sh
   ./scripts/install/setup.sh

Step 2: Verify Installation (1 min)
=====================================

.. code-block:: bash

   python3 -c "import neurostride; print('✅ Installed!')"
   python3 tests/unit/test_installation.py

Step 3: Train a Walking Policy (2 min - demo)
==============================================

This trains a small policy for demonstration:

.. code-block:: bash

   python3 src/train/train_locomotion.py \
       --robot unitree_g1 \
       --algo ppo \
       --timesteps 1000 \
       --save-path models/demo/

Expected output:

.. code-block:: bash

   ✅ Training started...
   Episode 10: Mean reward = 0.234
   Episode 50: Mean reward = 1.456
   🎉 Training complete! Model saved.

Step 4: Visualize Your Robot (optional)
=========================================

See your robot walking in simulation:

.. code-block:: bash

   python3 src/visualize/realtime_sim.py \
       --model models/demo/ppo_unitree_g1_final.zip \
       --render

A MuJoCo window should open showing the robot walking.

What's Next?
=============

You've completed the quick start! Now:

1. **Full Training**: Run with ``--timesteps 1_000_000`` for production model
2. **Vision-Language**: Try :doc:`/tutorials/vl_commands`
3. **Edge Deployment**: See :doc:`/deployment/edge`
4. **Custom Robot**: Follow :doc:`/advanced/custom_robot`

Troubleshooting
===============

MuJoCo License Error
----------------------

Get free license from `mujoco.org <https://mujoco.org/>`_ and place key at ``~/.mujoco/mjkey.txt``.

Import Errors
--------------

Reinstall in development mode:

.. code-block:: bash

   pip install -e .

ROS2 Issues
------------

ROS2 is optional. Disable ROS2 features:

.. code-block:: python

   # In your code
   from neurostride.ros2_bridge import disable_ros2
   disable_ros2()

Training Too Slow
-----------------

- Reduce ``--timesteps``
- Use smaller robot model
- Enable GPU: ``export MUJOCO_GL=egl``

Next Tutorials
==============

- :doc:`vl_commands` - Natural language robot control
- :doc:`advanced/training` - Advanced RL techniques
- :doc:`deployment/edge` - Deploy to Jetson

.. _api-reference:

===========
API Reference
===========

Complete Python API documentation for NeuroStride-VL.

.. toctree::
   :maxdepth: 2
   :caption: API Modules:

   neurostride
   environments
   agents
   perception
   ros2_bridge
   models
   utils

====================
Core Module: neurostride
====================

Main entry point for the library.

.. automodule:: neurostride
   :members:
   :undoc-members:
   :show-inheritance:

====================
Environments (neurostride.env)
====================

Reinforcement learning environments for bipedal robots.

BipedalEnv
===========

.. autoclass:: neurostride.env.BipedalEnv
   :members:
   :undoc-members:
   :show-inheritance:

RobotBase
==========

.. autoclass:: neurostride.env.robots.RobotBase
   :members:
   :undoc-members:
   :show-inheritance:

UnitreeG1
==========

.. autoclass:: neurostride.env.robots.UnitreeG1
   :members:
   :undoc-members:
   :show-inheritance:

====================
Agents (neurostride.agents)
====================

Reinforcement learning algorithms.

PPOAgent
=========

.. autoclass:: neurostride.agents.PPOAgent
   :members:
   :undoc-members:
   :show-inheritance:

SACAgent
=========

.. autoclass:: neurostride.agents.SACAgent
   :members:
   :undoc-members:
   :show-inheritance:

PolicyNetwork
==============

.. autoclass:: neurostride.agents.PolicyNetwork
   :members:
   :undoc-members:
   :show-inheritance:

====================
Perception (neurostride.perception)
====================

Vision-language model integration.

QwenVLAgent
============

.. autoclass:: neurostride.perception.QwenVLAgent
   :members:
   :undoc-members:
   :show-inheritance:

SceneParser
============

.. autoclass:: neurostride.perception.SceneParser
   :members:
   :undoc-members:
   :show-inheritance:

====================
ROS2 Bridge (neurostride.ros2_bridge)
====================

ROS2 communication for distributed deployment.

CommanderNode
===============

.. autoclass:: neurostride.ros2_bridge.CommanderNode
   :members:
   :undoc-members:
   :show-inheritance:

ExecutorNode
=============

.. autoclass:: neurostride.ros2_bridge.ExecutorNode
   :members:
   :undoc-members:
   :show-inheritance:

====================
Models (neurostride.models)
====================

Neural network architectures.

LocomotionPolicy
=================

.. autoclass:: neurostride.models.LocomotionPolicy
   :members:
   :undoc-members:
   :show-inheritance:

VLProcessor
=============

.. autoclass:: neurostride.models.VLProcessor
   :members:
   :undoc-members:
   :show-inheritance:

FusionNetwork
===============

.. autoclass:: neurostride.models.FusionNetwork
   :members:
   :undoc-members:
   :show-inheritance:

====================
Utilities (neurostride.utils)
====================

Helper functions and tools.

ConfigLoader
=============

.. autoclass:: neurostride.utils.ConfigLoader
   :members:
   :undoc-members:
   :show-inheritance:

Visualization
==============

.. automodule:: neurostride.utils.visualization
   :members:
   :undoc-members:
   :show-inheritance:

HardwareMonitor
=================

.. autoclass:: neurostride.utils.HardwareMonitor
   :members:
   :undoc-members:
   :show-inheritance:

.. _architecture-components:

====================
System Components
====================

Detailed overview of each NeuroStride-VL component.

Perception Module
==================

QwenVLAgent
-------------

The vision-language model that understands scenes and commands.

**Responsibilities:**
- Image preprocessing (resize, normalize)
- Tokenize text commands
- Run Qwen-2-VL inference
- Parse structured output

**Interface:**

.. code-block:: python

   from neurostride.perception import QwenVLAgent

   agent = QwenVLAgent(
       model_path="Qwen/Qwen-VL-2B-Chat",
       device="cuda:0"  # or "mps" for Mac
   )

   result = agent.analyze_scene(
       image="camera_frame.jpg",
       command="Walk to the red ball"
   )

**Output:**

.. code-block:: python

   {
       "objects": ["red_ball", "person", "wall"],
       "spatial": {"red_ball": "2m ahead", "person": "left"},
       "command": "linear.x=0.5, avoid left"
   }

RL Agents
===========

PPOAgent
----------

Proximal Policy Optimization for stable training.

**Key features:**
- Clip-based policy updates
- Value function as critic
- On-policy learning

**When to use:** Default choice, stable and reliable.

SACAgent
----------

Soft Actor-Critic for sample-efficient learning.

**Key features:**
- Off-policy learning (replay buffer)
- Entropy regularization
- Twin Q-networks

**When to use:** Limited data, need sample efficiency.

Policy Network
===============

.. code-block:: python

   class LocomotionPolicy(nn.Module):
       def __init__(self, obs_dim=377, act_dim=12, hidden_sizes=[256, 256]):
           super().__init__()
           self.net = MLP(obs_dim, act_dim, hidden_sizes)

       def forward(self, obs, deterministic=False):
           mu, log_std = self.net(obs)
           std = torch.exp(log_std)
           dist = Normal(mu, std)
           return dist.rsample() if not deterministic else mu

Input: 377-dim observation vector
Output: 12-dim action vector (joint torques)

ROS2 Bridge
=============

CommanderNode (Mac M2 Pro)
-----------------------------

.. code-block:: python

   from neurostride.ros2_bridge import CommanderNode

   node = CommanderNode(role="commander")
   node.send_command("Walk forward 2 meters")
   node.spin()

Responsibilities:
- Runs Qwen-VL model
- Publishes ``/cmd_vel`` (Twist messages)
- Subscribes to ``/robot/status``

ExecutorNode (Jetson Orin Nano)
---------------------------------

.. code-block:: python

   from neurostride.ros2_bridge import ExecutorNode

   node = ExecutorNode(role="executor")
   node.run_policy(policy_path="models/sac_policy.zip")
   node.spin()

Responsibilities:
- Receives ``/cmd_vel`` commands
- Runs SAC policy at 500Hz
- Publishes motor commands to ``/joint_torques``
- Subscribes to sensor data

Message Definitions
====================

``geometry_msgs/Twist`` - Velocity command:

.. code-block:: python

   Twist(
       linear=Vector3(x=0.5, y=0.0, z=0.0),
       angular=Vector3(x=0.0, y=0.0, z=0.0)
   )

Simulation Environment
=======================

BipedalEnv
============

Custom Gym environment wrapping MuJoCo.

.. code-block:: python

   from neurostride.env import BipedalEnv

   env = BipedalEnv(
       robot_type="unitree_g1",
       terrain="flat",
       reward_type="shaped"
   )

   obs = env.reset()
   action = policy(obs)
   next_obs, reward, done, info = env.step(action)

Observation Space (377-dim):

.. code-block:: python

   [
       # Robot state (12 joints × 3 = 36)
       joint_positions[12],
       joint_velocities[12],
       joint_torques[12],

       # IMU (6)
       orientation_quat[4],
       angular_velocity[3],
       linear_acceleration[3],

       # Previous action (12)
       last_action[12],

       # Command (3)
       target_velocity[3],

       # Feet contact (4)
       foot_contacts[4],

       # External forces (6)
       external_force[3],
       external_torque[3],

       # Terrain (optional, 300)
       heightfield[100, 100, 3]  # Flattened
   ]

Reward Function
================

Default reward (shaped):

.. math::

   r = w_1 \cdot r_{upright} + w_2 \cdot r_{velocity} + w_3 \cdot r_{energy} + w_4 \cdot r_{smooth}

Component weights:
- Upright: 0.35
- Velocity tracking: 0.30
- Energy efficiency: 0.20
- Smooth gait: 0.15

Models
======

LocomotionPolicy
-----------------

MLP-based policy network:

.. code-block:: python

   Input (377) → Linear(377→256) → ReLU
               → Linear(256→256) → ReLU
               → Linear(256→256) → ReLU
               → Split → Mu (256→12) + LogStd (256→12)

Total parameters: ~270k

VLProcessor
============

Vision-language encoder:

.. code-block:: python

   from neurostride.models import VLProcessor

   processor = VLProcessor(
       vision_model="Qwen/Qwen-VL-2B-Chat",
       freeze_vision=True  # For transfer learning
   )

   embedding = processor(image, text)

Utilities
==========

ConfigLoader
=============

Load YAML configurations:

.. code-block:: python

   from neurostride.utils import ConfigLoader

   config = ConfigLoader.load("configs/training/ppo_config.yaml")
   learning_rate = config.algorithm.learning_rate

Visualization
==============

Real-time MuJoCo viewer:

.. code-block:: python

   from neurostride.utils import visualize_policy

   visualize_policy(
       policy="models/policy.zip",
       robot="unitree_g1",
       render=True,
       record_video="output.mp4"
   )

HardwareMonitor
================

Monitor system resources:

.. code-block:: python

   from neurostride.utils import HardwareMonitor

   monitor = HardwareMonitor()
   print(f"GPU: {monitor.gpu_usage()}%")
   print(f"RAM: {monitor.ram_usage()} MB")
   print(f"Temp: {monitor.gpu_temp()}°C")

Component Interaction Diagram
==============================

.. mermaid:: ../../../src/architecture/component_interaction.mermaid
   :alt: Component Interaction

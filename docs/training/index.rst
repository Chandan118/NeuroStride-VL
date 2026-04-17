.. _training-guide:

==========
Training Guide
==========

Learn to train bipedal locomotion policies using reinforcement learning.

.. toctree::
   :maxdepth: 2
   :caption: Training Sections:

   basics
   advanced
   vl_finetuning
   evaluation

====================
Training Basics
====================

NeuroStride-VL uses **Stable-Baselines3** for reinforcement learning. This guide covers training walking policies from scratch.

Training Pipeline
==================

.. mermaid:: ../../src/agents/training_pipeline.mermaid
   :alt: Training Pipeline

The training loop:

1. **Initialize** environment and agent
2. **Collect** experiences by interacting with MuJoCo
3. **Compute** advantages and returns
4. **Update** policy network (PPO/SAC)
5. **Evaluate** performance
6. **Repeat** until convergence

Quick Training Command
=======================

.. code-block:: bash

   python3 src/train/train_locomotion.py \
       --robot unitree_g1 \
       --algo ppo \
       --timesteps 1_000_000 \
       --save-path models/checkpoints/

Parameters Explained
--------------------

- ``--robot``: Robot model (``unitree_g1``, ``digit``, or custom)
- ``--algo``: RL algorithm (``ppo``, ``sac``, ``td3``)
- ``--timesteps``: Total environment steps (more = better but slower)
- ``--save-path``: Where to save checkpoints

Training Output
================

During training, you'll see:

.. code-block:: bash

   ✅ Training started...
   Episode 100: Mean reward = 0.452
   Episode 500: Mean reward = 1.234
   Episode 1000: Mean reward = 2.891 ✅
   🎉 Training complete! Model saved.

Reward Interpretation
-----------------------

Reward values indicate walking quality:

- **< 0.5**: Falling frequently, poor balance
- **0.5 - 1.5**: Basic standing, occasional steps
- **1.5 - 2.5**: Stable walking, moderate speed
- **> 2.5**: Advanced locomotion, good speed and stability

Training Time Estimates
========================

| Robot | Algo | Timesteps | Time (M2 Pro) | Time (Jetson) |
|-------|------|-----------|---------------|---------------|
| Unitree G1 | PPO | 1M | 6.5h | 12h |
| Unitree G1 | SAC | 1M | 8.2h | 15h |
| Digit | TD3 | 1M | 7.1h | 13h |

Saving and Loading Models
===========================

Save automatically (via ``--save-path``) or manually:

.. code-block:: python

   from neurostride.agents import PPOAgent

   # Train
   agent.learn(total_timesteps=1_000_000)

   # Save
   agent.save("models/checkpoints/my_policy.zip")

   # Load
   agent = PPOAgent.load("models/checkpoints/my_policy.zip")

Checkpoint Management
======================

NeuroStride-VL saves checkpoints automatically:

.. code-block:: bash

   models/checkpoints/
   ├── ppo_latest.zip          # Most recent
   ├── ppo_best.zip            # Best reward
   ├── ppo_unitree_g1_final.zip # Final model
   └── training_log.csv        # Metrics history

Monitoring Training
====================

Use TensorBoard:

.. code-block:: bash

   tensorboard --logdir=models/tensorboard/

Open http://localhost:6006 in browser.

Metrics tracked:
- Episode reward mean/min/max
- Episode length
- Policy loss
- Value loss
- Learning rate

Hyperparameter Tuning
======================

Key hyperparameters in ``configs/training/ppo_config.yaml``:

.. code-block:: yaml

   learning_rate: 3e-4        # Adam optimizer step size
   n_steps: 2048             # Steps per rollout
   batch_size: 64           # Mini-batch size
   n_epochs: 10             # Policy updates per rollout
   gamma: 0.99              # Discount factor
   gae_lambda: 0.95         # GAE parameter
   clip_range: 0.2          # PPO clip range
   ent_coef: 0.01           # Entropy coefficient

Recommendations:

- **Higher learning rate** (3e-4) for faster initial learning
- **Lower learning rate** (1e-4) for fine-tuning
- **More steps** (4096) for complex robots
- **Less steps** (1024) for simple environments

Early Stopping
==============

Stop training when performance plateaus:

.. code-block:: python

   from neurostride.train import EarlyStopper

   stopper = EarlyStopper(patience=10, min_delta=0.01)

   for episode in range(max_episodes):
       reward = train_episode()
       if stopper.should_stop(reward):
           print(f"Early stopping at episode {episode}")
           break

Common Issues
=============

Training is Unstable
---------------------

- Reduce learning rate
- Increase batch size
- Normalize observations (default: enabled)
- Check reward scaling (should be ~1-10 range)

Robot Falls Immediately
------------------------

- Increase upright reward weight
- Reduce control penalty
- Add more random initialization
- Start with simpler terrain

Training Too Slow
------------------

- Increase ``n_steps`` (larger rollouts)
- Use GPU if available
- Reduce observation dimension
- Use SAC (sample-efficient but slower per step)

No Improvement After 1M Steps
-------------------------------

- Check reward function design
- Increase network capacity (more layers/units)
- Try different algorithm (SAC vs PPO)
- Inspect environment for bugs

Next Steps
==========

- Advanced training: :doc:`advanced/training`
- Vision-language finetuning: :doc:`vl_finetuning`
- Evaluation metrics: :doc:`evaluation`

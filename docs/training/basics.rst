.. _training-basics:

==========
Training Basics
==========

Fundamentals of RL training for bipedal locomotion.

RL Algorithms
==============

PPO (Proximal Policy Optimization)
------------------------------------

- **Type**: On-policy
- **Sample efficiency**: Low
- **Stability**: High
- **Use case**: Default choice, reliable

**Pros:**
✅ Stable training
✅ Easy to tune
✅ Good performance

**Cons:**
❌ Requires many samples
❌ Slower per step

SAC (Soft Actor-Critic)
-------------------------

- **Type**: Off-policy
- **Sample efficiency**: High
- **Stability**: Medium
- **Use case**: Limited data, need efficiency

**Pros:**
✅ Sample efficient
✅ Stochastic policy (good exploration)
✅ Entropy regularization

**Cons:**
❌ More hyperparameters
❌ Can be unstable

TD3 (Twin Delayed DDPG)
-------------------------

- **Type**: Off-policy
- **Sample efficiency**: High
- **Stability**: Medium-High
- **Use case**: Continuous control, deterministic policies

Training Configuration
========================

Key parameters in ``configs/training/ppo_config.yaml``:

.. code-block:: yaml

   # Network
   policy_kwargs:
     net_arch: [256, 256]  # Hidden layer sizes
     activation_fn: relu

   # Training
   n_steps: 2048          # Steps per rollout
   batch_size: 64         # Minibatch size
   n_epochs: 10           # Policy updates per rollout
   gamma: 0.99           # Discount factor
   gae_lambda: 0.95      # GAE parameter
   clip_range: 0.2       # PPO clip range
   ent_coef: 0.01        # Entropy coefficient

   # Optimization
   learning_rate: 3.0e-4
   max_grad_norm: 0.5

Reward Shaping
================

Designing effective reward functions:

.. code-block:: python

   def compute_reward(env):
       # 1. Stay upright (most important)
       upright = -abs(env.robot.torso_pitch)

       # 2. Move forward
       velocity = env.current_vel_x - env.target_vel

       # 3. Minimize energy
       energy = -np.sum(np.abs(env.torques * env.joint_vels))

       # 4. Smooth actions
       smoothness = -np.sum(np.abs(env.action - env.last_action))

       return 0.4 * upright + 0.3 * velocity + 0.2 * energy + 0.1 * smoothness

Reward Weight Tips:
- Upright: 0.3-0.5 (prevent falling)
- Velocity: 0.2-0.4 (task completion)
- Energy: 0.1-0.2 (efficiency)
- Smoothness: 0.05-0.15 (natural motion)

Curriculum Learning
====================

Start simple, increase difficulty:

.. code-block:: python

   from neurostride.env import CurriculumWrapper

   env = BipedalEnv(robot="unitree_g1")
   curriculum = CurriculumWrapper(env, stages=[
       {"terrain": "flat", "max_steps": 1000},
       {"terrain": "flat_obstacles", "max_steps": 2000},
       {"terrain": "slope", "max_steps": 3000},
       {"terrain": "stairs", "max_steps": 5000}
   ])

Checkpointing
==============

Auto-save best models:

.. code-block:: python

   from neurostride.train import CheckpointCallback

   callback = CheckpointCallback(
       save_freq=10000,
       save_path="models/checkpoints/",
       name_prefix="ppo_unitree_g1"
   )
   model.learn(total_timesteps=1e6, callback=callback)

Evaluation
===========

After training:

.. code-block:: python

   from neurostride.train import evaluate_policy

   mean_reward, std = evaluate_policy(
       model,
       env,
       n_eval_episodes=10,
       deterministic=True
   )

   print(f"Mean reward: {mean_reward:.2f} ± {std:.2f}")

Debugging Tips
===============

Robot doesn't move
-------------------
→ Increase forward velocity reward weight
→ Check action scaling (should be [-1, 1] normalized)
→ Reduce control penalty

Robot falls immediately
------------------------
→ Increase upright reward
→ Add initial stabilization period
→ Reduce maximum torque limits

Training is noisy/unstable
---------------------------
→ Increase batch size
→ Decrease learning rate
→ Enable gradient clipping
→ Normalize observations

No improvement after many steps
---------------------------------
→ Check reward scale (should be ~1-10 range)
→ Increase network capacity
→ Try different algorithm (SAC)
→ Inspect environment dynamics

Hyperparameter Search
======================

Use Optuna for automated tuning:

.. code-block:: python

   from neurostride.hyperparam import optimize_hyperparams

   study = optimize_hyperparams(
       env_class=BipedalEnv,
       algo="ppo",
       n_trials=50,
       timeout_hours=4
   )

   print(f"Best params: {study.best_params}")

Next: Advanced Training
========================

- :doc:`advanced/training` - Advanced techniques
- :doc:`vl_finetuning` - Vision-language finetuning
- :doc:`/deployment/edge` - Edge deployment

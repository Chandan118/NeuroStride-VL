#!/usr/bin/env python3
"""
NeuroStride-VL Quick Start Example
====================================
Demonstrates basic bipedal robot training and inference workflow
"""

import sys
import os

# Add project path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from neurostride.env import make_env
from neurostride.agents import create_agent


def main():
    print("=" * 60)
    print("NeuroStride-VL Quick Start Example")
    print("=" * 60)

    # 1. Create environment
    print("\n1. Creating training environment...")
    env = make_env(env_name="unitree_g1", render_mode=None, seed=42)
    print(f"   ✅ Environment created")
    print(f"   Observation space: {env.observation_space}")
    print(f"   Action space: {env.action_space}")

    # 2. Create agent
    print("\n2. Creating PPO agent...")
    agent = create_agent(algo="ppo", env_name="unitree_g1", total_timesteps=10000)
    print(f"   ✅ Agent created")

    # 3. Quick training (small timesteps for demo)
    print("\n3. Starting quick training (10,000 steps)...")
    print("   Note: This is a demo; full training requires 1M+ steps")
    agent.train(total_timesteps=10000)

    # 4. Evaluate performance
    print("\n4. Evaluating model performance...")
    mean_reward, std_reward = agent.evaluate(n_episodes=3)
    print(f"   Mean reward: {mean_reward:.2f} ± {std_reward:.2f}")

    # 5. Test inference
    print("\n5. Testing policy inference...")
    obs, _ = env.reset()
    action = agent.predict(obs)
    print(f"   Observation dim: {obs.shape}")
    print(f"   Action dim: {action.shape}")
    print(f"   Action range: [{action.min():.3f}, {action.max():.3f}]")

    # 6. Save model
    print("\n6. Saving model...")
    agent.save("models/checkpoints/demo_ppo")
    print(f"   ✅ Model saved")

    print("\n" + "=" * 60)
    print("🎉 Quick start example complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Full training: python scripts/train/train_locomotion.sh --algo ppo --timesteps 1000000")
    print("  2. Deploy to Jetson: ./scripts/deploy/deploy_to_jetson.sh --host <JETSON_IP>")
    print("  3. View docs: cat README.md")
    print("")


if __name__ == "__main__":
    main()

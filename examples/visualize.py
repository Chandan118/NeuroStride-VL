#!/usr/bin/env python3
"""
NeuroStride-VL Real-time Visualization Example
================================================
Visualize bipedal robot motion using MuJoCo
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import time
import numpy as np
from neurostride.env import make_env
from neurostride.agents import create_agent


def main():
    print("NeuroStride-VL Real-time Visualization")
    print("=" * 50)

    # Create environment with rendering
    env = make_env(env_name="unitree_g1", render_mode="human", seed=42)

    # Load trained model (or use random policy)
    print("Loading policy...")
    try:
        agent = create_agent(algo="sac", env_name="unitree_g1")
        agent.load("models/checkpoints/demo_ppo")  # Try loading demo model
        print("✅ Policy model loaded")
    except:
        print("⚠️  No model found, using random policy")

    # Run episodes
    n_episodes = 3
    for episode in range(n_episodes):
        print(f"\nEpisode {episode + 1}/{n_episodes}")

        obs, _ = env.reset()
        done = False
        truncated = False
        total_reward = 0
        step = 0

        while not (done or truncated):
            # Select action
            if 'agent' in locals():
                action = agent.predict(obs, deterministic=True)
            else:
                action = env.action_space.sample()

            # Step
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
            step += 1

            # Print progress
            if step % 100 == 0:
                print(f"  Step {step}, Reward: {reward:.3f}, Total: {total_reward:.2f}")

        print(f"  ✅ Episode ended: Steps={step}, Total Reward={total_reward:.2f}")

    env.close()
    print("\n🎉 Visualization complete!")


if __name__ == "__main__":
    main()

"""
NeuroStride-VL Test Suite
==========================
Unit and integration tests
"""

import unittest
import numpy as np


class TestEnvironment(unittest.TestCase):
    """Test environment module"""

    def test_env_creation(self):
        """Test environment creation"""
        from neurostride.env import make_env
        env = make_env(env_name="unitree_g1")
        self.assertIsNotNone(env)
        self.assertEqual(env.observation_space.shape[0], 70)
        self.assertEqual(env.action_space.shape[0], 23)

    def test_env_step(self):
        """Test environment step"""
        from neurostride.env import make_env
        env = make_env(env_name="unitree_g1")
        obs, _ = env.reset()
        action = env.action_space.sample()
        obs_next, reward, done, truncated, info = env.step(action)
        self.assertEqual(obs.shape, obs_next.shape)
        self.assertIsInstance(reward, float)


class TestAgents(unittest.TestCase):
    """Test agent module"""

    def test_agent_creation(self):
        """Test agent creation"""
        from neurostride.agents import create_agent
        agent = create_agent(algo="ppo", total_timesteps=100)
        self.assertIsNotNone(agent)

    def test_agent_predict(self):
        """Test agent prediction"""
        from neurostride.env import make_env
        from neurostride.agents import create_agent
        env = make_env()
        agent = create_agent(algo="sac")
        obs, _ = env.reset()
        action = agent.predict(obs)
        self.assertEqual(action.shape[0], env.action_space.shape[0])


class TestPerception(unittest.TestCase):
    """Test perception module"""

    def test_vl_config(self):
        """Test VLM configuration"""
        from neurostride.perception import VLConfig
        config = VLConfig()
        self.assertEqual(config.model_path, "Qwen/Qwen-VL-2B-Chat")


if __name__ == "__main__":
    unittest.main()

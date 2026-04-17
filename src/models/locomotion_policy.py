"""
NeuroStride-VL: Locomotion Policy Network
=========================================
PyTorch-based policy network architecture
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class LocomotionPolicy(nn.Module):
    """
    Bipedal robot walking policy network

    Input: State observation (joint positions, velocities, IMU, target velocity)
    Output: Actions (joint torques)
    """

    def __init__(
        self,
        obs_dim: int = 70,
        action_dim: int = 23,
        hidden_sizes: Tuple[int, ...] = (256, 256),
        activation: str = "tanh",
    ):
        super().__init__()

        # Activation function
        if activation == "tanh":
            self.activation = nn.Tanh
        elif activation == "relu":
            self.activation = nn.ReLU
        elif activation == "elu":
            self.activation = nn.ELU
        else:
            raise ValueError(f"Unsupported activation: {activation}")

        # Build network
        layers = []
        prev_size = obs_dim

        for size in hidden_sizes:
            layers.append(nn.Linear(prev_size, size))
            layers.append(self.activation())
            prev_size = size

        self.shared_net = nn.Sequential(*layers)

        # Policy head (Actor)
        self.policy_mean = nn.Linear(prev_size, action_dim)
        self.policy_logstd = nn.Parameter(torch.zeros(action_dim))

        # Value head (Critic)
        self.value_net = nn.Linear(prev_size, 1)

        # Initialize
        self._init_weights()

    def _init_weights(self):
        """Initialize network weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.orthogonal_(module.weight, gain=nn.init.calculate_gain('tanh'))
                nn.init.constant_(module.bias, 0)

    def forward(
        self,
        obs: torch.Tensor,
        deterministic: bool = False
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass

        Args:
            obs: Observation tensor (batch, obs_dim)
            deterministic: Whether to use deterministic policy

        Returns:
            action: Actions (batch, action_dim)
            log_prob: Log probabilities (batch,)
            value: Value estimates (batch,)
        """
        # Shared features
        features = self.shared_net(obs)

        # Policy distribution
        mean = self.policy_mean(features)
        std = torch.exp(self.policy_logstd).expand_as(mean)

        # Create normal distribution
        dist = torch.distributions.Normal(mean, std)

        # Sample action
        if deterministic:
            action = mean
        else:
            action = dist.rsample()

        # Compute log probability
        log_prob = dist.log_prob(action).sum(dim=-1)

        # Compute entropy
        entropy = dist.entropy().sum(dim=-1)

        # Compute value
        value = self.value_net(features).squeeze(-1)

        return action, log_prob, entropy

    def evaluate_actions(
        self,
        obs: torch.Tensor,
        actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions (for training)

        Args:
            obs: Observations (batch, obs_dim)
            actions: Actions to evaluate (batch, action_dim)

        Returns:
            values: Value estimates (batch,)
            log_prob: Log probabilities (batch,)
            entropy: Entropy (batch,)
        """
        # Shared features
        features = self.shared_net(obs)

        # Policy distribution
        mean = self.policy_mean(features)
        std = torch.exp(self.policy_logstd).expand_as(mean)
        dist = torch.distributions.Normal(mean, std)

        # Evaluate
        log_prob = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        value = self.value_net(features).squeeze(-1)

        return value, log_prob, entropy

    def get_distribution(self, obs: torch.Tensor):
        """Get action distribution"""
        features = self.shared_net(obs)
        mean = self.policy_mean(features)
        std = torch.exp(self.policy_logstd).expand_as(mean)
        return torch.distributions.Normal(mean, std)


# Simplified policy (inference only)
class SimplePolicy(nn.Module):
    """Simplified policy network for inference only"""

    def __init__(self, obs_dim: int = 70, action_dim: int = 23):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, action_dim),
            nn.Tanh(),  # Output range [-1, 1]
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs)


if __name__ == "__main__":
    # Test network
    print("Testing LocomotionPolicy...")

    batch_size = 32
    obs_dim = 70
    action_dim = 23

    policy = LocomotionPolicy(obs_dim, action_dim)

    obs = torch.randn(batch_size, obs_dim)
    action, log_prob, value = policy(obs)

    print(f"Input: {obs.shape}")
    print(f"Action: {action.shape}")
    print(f"Log prob: {log_prob.shape}")
    print(f"Value: {value.shape}")

    # Evaluate actions
    test_actions = torch.randn(batch_size, action_dim)
    value2, log_prob2, entropy = policy.evaluate_actions(obs, test_actions)
    print(f"Evaluated log prob: {log_prob2.shape}")
    print(f"熵: {entropy.shape}")

    print("✅ 网络测试通过！")

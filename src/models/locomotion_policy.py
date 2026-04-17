"""
NeuroStride-VL: 行走策略网络
=============================
基于 PyTorch 的策略网络架构
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class LocomotionPolicy(nn.Module):
    """
    双足机器人行走策略网络

    输入: 状态观测 (关节位置、速度、IMU、目标速度)
    输出: 动作 (关节扭矩)
    """

    def __init__(
        self,
        obs_dim: int = 70,
        action_dim: int = 23,
        hidden_sizes: Tuple[int, ...] = (256, 256),
        activation: str = "tanh",
    ):
        super().__init__()

        # 激活函数
        if activation == "tanh":
            self.activation = nn.Tanh
        elif activation == "relu":
            self.activation = nn.ReLU
        elif activation == "elu":
            self.activation = nn.ELU
        else:
            raise ValueError(f"不支持的激活函数: {activation}")

        # 构建网络
        layers = []
        prev_size = obs_dim

        for size in hidden_sizes:
            layers.append(nn.Linear(prev_size, size))
            layers.append(self.activation())
            prev_size = size

        self.shared_net = nn.Sequential(*layers)

        # 策略头 (Actor)
        self.policy_mean = nn.Linear(prev_size, action_dim)
        self.policy_logstd = nn.Parameter(torch.zeros(action_dim))

        # 价值头 (Critic)
        self.value_net = nn.Linear(prev_size, 1)

        # 初始化
        self._init_weights()

    def _init_weights(self):
        """初始化网络权重"""
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
        前向传播

        Args:
            obs: 观测张量 (batch, obs_dim)
            deterministic: 是否使用确定性策略

        Returns:
            action: 动作 (batch, action_dim)
            log_prob: 对数概率 (batch,)
            value: 价值估计 (batch,)
        """
        # 共享特征
        features = self.shared_net(obs)

        # 策略分布
        mean = self.policy_mean(features)
        std = torch.exp(self.policy_logstd).expand_as(mean)

        # 创建正态分布
        dist = torch.distributions.Normal(mean, std)

        # 采样动作
        if deterministic:
            action = mean
        else:
            action = dist.rsample()

        # 计算对数概率
        log_prob = dist.log_prob(action).sum(dim=-1)

        # 价值估计
        value = self.value_net(features).squeeze(-1)

        return action, log_prob, value

    def evaluate_actions(
        self,
        obs: torch.Tensor,
        actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        评估给定动作的对数概率和熵

        Args:
            obs: 观测张量
            actions: 动作张量

        Returns:
            log_prob: 对数概率
            entropy: 熵
            value: 价值估计
        """
        features = self.shared_net(obs)

        mean = self.policy_mean(features)
        std = torch.exp(self.policy_logstd).expand_as(mean)
        dist = torch.distributions.Normal(mean, std)

        log_prob = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)

        value = self.value_net(features).squeeze(-1)

        return log_prob, entropy, value

    def get_value(self, obs: torch.Tensor) -> torch.Tensor:
        """仅获取价值估计"""
        features = self.shared_net(obs)
        return self.value_net(features).squeeze(-1)


# 简化版策略（仅用于推理）
class SimplePolicy(nn.Module):
    """简化策略网络，仅用于推理阶段"""

    def __init__(self, obs_dim: int = 70, action_dim: int = 23):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, action_dim),
            nn.Tanh(),  # 输出范围 [-1, 1]
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs)


if __name__ == "__main__":
    # 测试网络
    print("测试 LocomotionPolicy...")

    batch_size = 32
    obs_dim = 70
    action_dim = 23

    policy = LocomotionPolicy(obs_dim, action_dim)

    obs = torch.randn(batch_size, obs_dim)
    action, log_prob, value = policy(obs)

    print(f"输入: {obs.shape}")
    print(f"动作: {action.shape}")
    print(f"对数概率: {log_prob.shape}")
    print(f"价值: {value.shape}")

    # 评估动作
    test_actions = torch.randn(batch_size, action_dim)
    log_prob2, entropy, value2 = policy.evaluate_actions(obs, test_actions)
    print(f"评估对数概率: {log_prob2.shape}")
    print(f"熵: {entropy.shape}")

    print("✅ 网络测试通过！")

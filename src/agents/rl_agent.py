"""
NeuroStride-VL: Reinforcement Learning Agent
============================================
PPO and SAC algorithm implementations based on Stable-Baselines3

Supported algorithms:
- PPO (Proximal Policy Optimization)
- SAC (Soft Actor-Critic)

Authors: NeuroStride-VL Team
"""

import os
import time
import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field

from stable_baselines3 import PPO, SAC
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.policies import MlpPolicy
from stable_baselines3.common.evaluation import evaluate_policy

from neurostride.env.bipedal_env import BipedalEnv, RobotConfig, make_env


@dataclass
class TrainingConfig:
    """训练配置"""
    # 算法选择
    algo: str = "ppo"  # "ppo" 或 "sac"

    # 环境配置
    env_name: str = "unitree_g1"
    env_kwargs: Dict[str, Any] = field(default_factory=dict)

    # 网络架构
    policy_kwargs: Dict[str, Any] = field(default_factory=lambda: {
        "net_arch": [dict(pi=[256, 256], vf=[256, 256])],  # PPO
        # "net_arch": [256, 256],  # SAC
        "activation_fn": torch.nn.Tanh,
    })

    # PPO 特定参数
    ppo_params: Dict[str, Any] = field(default_factory=lambda: {
        "learning_rate": 3e-4,
        "n_steps": 2048,
        "batch_size": 64,
        "n_epochs": 10,
        "gamma": 0.99,
        "gae_lambda": 0.95,
        "clip_range": 0.2,
        "clip_range_vf": None,
        "ent_coef": 0.01,
        "vf_coef": 0.5,
        "max_grad_norm": 0.5,
    })

    # SAC 特定参数
    sac_params: Dict[str, Any] = field(default_factory=lambda: {
        "learning_rate": 3e-4,
        "buffer_size": 1_000_000,
        "learning_starts": 10000,
        "batch_size": 256,
        "tau": 0.005,
        "gamma": 0.99,
        "train_freq": 1,
        "gradient_steps": 1,
        "ent_coef": "auto",
        "target_update_interval": 1,
    })

    # 训练参数
    total_timesteps: int = 1_000_000
    eval_freq: int = 10000
    n_eval_episodes: int = 10
    save_freq: int = 50000

    # 日志
    log_dir: str = "logs/"
    model_dir: str = "models/checkpoints/"
    tensorboard_log: str = "runs/"

    # 随机种子
    seed: Optional[int] = 42

    # 设备
    device: str = "auto"  # "auto", "cuda", "mps", "cpu"


class CustomCallback(BaseCallback):
    """
    自定义训练回调
    用于记录详细的训练指标和定期保存模型
    """

    def __init__(self, verbose: int = 0, save_freq: int = 50000, model_dir: str = "models/"):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # 指标记录
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0

    def _on_step(self) -> bool:
        # 累计当前episode的奖励
        self.current_episode_reward += self.locals["rewards"][0]
        self.current_episode_length += 1

        # 检查episode是否结束
        if self.locals["dones"][0]:
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            self.current_episode_reward = 0
            self.current_episode_length = 0

        # 定期保存模型
        if self.n_calls % self.save_freq == 0:
            model_path = self.model_dir / f"{self.model.__class__.__name__}_step_{self.n_calls}"
            self.model.save(str(model_path))

            # 保存训练指标
            metrics = {
                "timestep": self.n_calls,
                "episode_rewards": self.episode_rewards[-100:],  # 最近100个episode
                "episode_lengths": self.episode_lengths[-100:],
                "mean_reward_100": np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            }
            with open(self.model_dir / "metrics.json", "w") as f:
                json.dump(metrics, f, indent=2)

        return True


class RLAgent:
    """
    强化学习智能体基类

    功能:
    - 环境创建和包装
    - 模型训练和评估
    - 模型保存和加载
    - 训练监控
    """

    def __init__(
        self,
        config: TrainingConfig,
        env: Optional[BipedalEnv] = None,
    ):
        """
        初始化 RL 智能体

        Args:
            config: 训练配置
            env: 环境实例（None则创建新环境）
        """
        self.config = config
        self.env = env or self._create_env()

        # 创建日志目录
        self.log_dir = Path(config.log_dir) / f"{config.algo}_{config.env_name}_{int(time.time())}"
        self.model_dir = Path(config.model_dir) / f"{config.algo}_{config.env_name}"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # 保存配置
        with open(self.log_dir / "config.json", "w") as f:
            json.dump(self._config_to_dict(config), f, indent=2)

        # 初始化模型（子类实现）
        self.model = None

        log_info(f"RLAgent 初始化完成")
        log_info(f"日志目录: {self.log_dir}")
        log_info(f"模型目录: {self.model_dir}")

    def _create_env(self) -> DummyVecEnv:
        """创建并包装环境"""
        def make_env_fn():
            env = make_env(
                env_name=self.config.env_name,
                render_mode=None,
                seed=self.config.seed,
                **self.config.env_kwargs
            )
            env = Monitor(env, str(self.log_dir))
            return env

        # 创建向量化环境（单个环境）
        env = DummyVecEnv([make_env_fn])

        # 归一化观测和奖励
        env = VecNormalize(
            env,
            norm_obs=True,
            norm_reward=True,
            clip_obs=10.0,
            clip_reward=10.0,
        )

        return env

    def _create_model(self):
        """创建算法模型（抽象方法）"""
        raise NotImplementedError

    def train(self, total_timesteps: Optional[int] = None):
        """
        训练模型

        Args:
            total_timesteps: 总训练步数（None则使用配置值）
        """
        if self.model is None:
            self.model = self._create_model()

        total_timesteps = total_timesteps or self.config.total_timesteps

        log_info(f"开始训练 {self.config.algo.upper()}...")
        log_info(f"总步数: {total_timesteps:,}")

        # 自定义回调
        custom_callback = CustomCallback(
            save_freq=self.config.save_freq,
            model_dir=str(self.model_dir)
        )

        # 评估回调
        eval_callback = EvalCallback(
            eval_env=self._create_eval_env(),
            best_model_save_path=str(self.model_dir),
            log_path=str(self.log_dir),
            eval_freq=self.config.eval_freq,
            n_eval_episodes=self.config.n_eval_episodes,
            deterministic=True,
            render=False,
        )

        # 开始训练
        try:
            self.model.learn(
                total_timesteps=total_timesteps,
                callback=[custom_callback, eval_callback],
                tb_log_name=f"{self.config.algo}_{self.config.env_name}",
                progress_bar=True,
            )
        except KeyboardInterrupt:
            log_warning("训练被用户中断")
        finally:
            # 保存最终模型
            final_path = self.model_dir / f"{self.config.algo}_final"
            self.model.save(str(final_path))
            log_success(f"最终模型已保存: {final_path}")

    def _create_eval_env(self) -> DummyVecEnv:
        """创建评估环境"""
        def make_eval_env():
            env = make_env(
                env_name=self.config.env_name,
                render_mode=None,
                seed=self.config.seed + 1000,  # 不同种子
                **self.config.env_kwargs
            )
            return env

        eval_env = DummyVecEnv([make_eval_env])
        eval_env = VecNormalize(
            eval_env,
            norm_obs=True,
            norm_reward=False,  # 评估时不归一化奖励
            clip_obs=10.0,
        )
        return eval_env

    def evaluate(self, n_episodes: int = 10) -> Tuple[float, float]:
        """
        评估模型性能

        Returns:
            mean_reward: 平均奖励
            std_reward: 奖励标准差
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train()")

        eval_env = self._create_eval_env()
        rewards, lengths = evaluate_policy(
            self.model,
            eval_env,
            n_eval_episodes=n_episodes,
            deterministic=True,
            render=False,
        )

        mean_reward = np.mean(rewards)
        std_reward = np.std(rewards)

        log_info(f"评估结果 ({n_episodes} 回合):")
        log_info(f"  平均奖励: {mean_reward:.2f} ± {std_reward:.2f}")
        log_info(f"  平均长度: {np.mean(lengths):.1f} 步")

        return mean_reward, std_reward

    def predict(self, observation: np.ndarray, deterministic: bool = True) -> np.ndarray:
        """
        预测动作

        Args:
            observation: 状态观测
            deterministic: 是否确定性策略

        Returns:
            action: 动作
        """
        if self.model is None:
            raise ValueError("模型未加载")

        action, _states = self.model.predict(observation, deterministic=deterministic)
        return action

    def save(self, path: str):
        """保存模型"""
        if self.model is None:
            raise ValueError("没有模型可保存")

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        log_success(f"模型已保存: {path}")

    def load(self, path: str):
        """加载模型"""
        if self.config.algo == "ppo":
            self.model = PPO.load(path, env=self.env)
        elif self.config.algo == "sac":
            self.model = SAC.load(path, env=self.env)
        else:
            raise ValueError(f"不支持的算法: {self.config.algo}")

        log_success(f"模型已加载: {path}")

    def _config_to_dict(self, config: TrainingConfig) -> Dict:
        """配置对象转字典"""
        return {
            "algo": config.algo,
            "env_name": config.env_name,
            "total_timesteps": config.total_timesteps,
            "seed": config.seed,
            "device": config.device,
            "policy_kwargs": config.policy_kwargs,
            "ppo_params": config.ppo_params if config.algo == "ppo" else None,
            "sac_params": config.sac_params if config.algo == "sac" else None,
        }


class PPOAgent(RLAgent):
    """PPO 智能体"""

    def _create_model(self):
        """创建 PPO 模型"""
        ppo_kwargs = {
            "policy": "MlpPolicy",
            "env": self.env,
            "policy_kwargs": self.config.policy_kwargs,
            "verbose": 1,
            "tensorboard_log": str(self.config.tensorboard_log),
            "device": self._get_device(),
            **self.config.ppo_params
        }

        model = PPO(**ppo_kwargs)
        log_success("PPO 模型创建完成")

        # 打印网络结构
        print(f"\n策略网络结构:")
        print(model.policy)

        return model

    def _get_device(self) -> str:
        """自动选择设备"""
        if self.config.device != "auto":
            return self.config.device

        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"


class SACAgent(RLAgent):
    """SAC 智能体"""

    def _create_model(self):
        """创建 SAC 模型"""
        sac_kwargs = {
            "policy": "MlpPolicy",
            "env": self.env,
            "policy_kwargs": self.config.policy_kwargs,
            "verbose": 1,
            "tensorboard_log": str(self.config.tensorboard_log),
            "device": self._get_device(),
            **self.config.sac_params
        }

        model = SAC(**sac_kwargs)
        log_success("SAC 模型创建完成")

        return model

    def _get_device(self) -> str:
        """自动选择设备"""
        if self.config.device != "auto":
            return self.config.device

        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"


# ==================== 辅助函数 ====================

def create_agent(algo: str, **kwargs) -> RLAgent:
    """
    快速创建智能体

    Args:
        algo: 算法名称 ("ppo" 或 "sac")
        **kwargs: 训练配置参数

    Returns:
        智能体实例
    """
    config = TrainingConfig(algo=algo, **kwargs)

    if algo.lower() == "ppo":
        return PPOAgent(config)
    elif algo.lower() == "sac":
        return SACAgent(config)
    else:
        raise ValueError(f"不支持的算法: {algo}。可选: ppo, sac")


def check_environment(env: BipedalEnv) -> bool:
    """
    检查环境是否符合 Gym 规范

    Returns:
        True 如果环境通过检查
    """
    log_info("检查环境兼容性...")
    try:
        check_env(env, warn=True, skip_render_check=True)
        log_success("环境检查通过 ✅")
        return True
    except Exception as e:
        log_error(f"环境检查失败: {e}")
        return False


# ==================== 快速训练脚本 ====================

def quick_train(
    env_name: str = "unitree_g1",
    algo: str = "ppo",
    timesteps: int = 100_000,
    seed: int = 42,
):
    """
    快速训练演示（用于测试）

    Args:
        env_name: 环境名称
        algo: 算法
        timesteps: 训练步数
        seed: 随机种子
    """
    print("=" * 60)
    print(f"NeuroStride-VL 快速训练: {algo.upper()} on {env_name}")
    print("=" * 60)

    # 创建配置
    config = TrainingConfig(
        algo=algo,
        env_name=env_name,
        total_timesteps=timesteps,
        seed=seed,
        policy_kwargs={"net_arch": [64, 64]},  # 小网络快速测试
    )

    # 创建智能体
    if algo == "ppo":
        agent = PPOAgent(config)
    else:
        agent = SACAgent(config)

    # 检查环境
    check_environment(agent.env)

    # 训练
    agent.train()

    # 评估
    mean_reward, std_reward = agent.evaluate(n_episodes=5)
    print(f"\n��终性能: {mean_reward:.2f} ± {std_reward:.2f}")

    return agent


# ==================== 主程序 ====================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("NeuroStride-VL: RL Agent 模块测试")
    print("=" * 60)

    # 解析命令行参数
    algo = sys.argv[1] if len(sys.argv) > 1 else "ppo"
    timesteps = int(sys.argv[2]) if len(sys.argv) > 2 else 10000

    print(f"\n算法: {algo.upper()}")
    print(f"训练步数: {timesteps:,}")

    # 运行快速训练
    agent = quick_train(algo=algo, timesteps=timesteps, seed=42)

    print("\n✅ RL Agent 模块测试完成！")

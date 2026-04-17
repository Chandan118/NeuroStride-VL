"""
NeuroStride-VL 可视化工具
=========================
用于训练曲线绘制和视频生成
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional


def plot_training_curves(
    rewards: List[float],
    lengths: List[float],
    losses: Optional[List[float]] = None,
    title: str = "Training Curves",
    save_path: Optional[str] = None,
):
    """
    绘制训练曲线

    Args:
        rewards: 每回合奖励列表
        lengths: 每回合步数列表
        losses: 损失值列表（可选）
        title: 图表标题
        save_path: 保存路径（None则显示）
    """
    fig, axes = plt.subplots(1, 3 if losses else 2, figsize=(12, 4))

    # 奖励曲线
    axes[0].plot(rewards, alpha=0.6, label='Episode Reward')
    axes[0].plot(
        np.convolve(rewards, np.ones(100)/100, mode='valid'),
        color='red', linewidth=2, label='Moving Avg (100)'
    )
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Reward')
    axes[0].set_title('Training Rewards')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 回合长度曲线
    axes[1].plot(lengths, alpha=0.6, label='Episode Length')
    axes[1].set_xlabel('Episode')
    axes[1].set_ylabel('Steps')
    axes[1].set_title('Episode Lengths')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 损失曲线（如果有）
    if losses and len(axes) > 2:
        axes[2].plot(losses, alpha=0.6, label='Loss')
        axes[2].set_xlabel('Update')
        axes[2].set_ylabel('Loss')
        axes[2].set_title('Policy Loss')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    else:
        plt.show()

    plt.close()


def render_video(
    frames: List[np.ndarray],
    output_path: str,
    fps: int = 30,
):
    """
    将帧序列渲染为视频

    Args:
        frames: 帧列表 (H, W, 3) uint8
        output_path: 输出视频路径
        fps: 帧率
    """
    import cv2

    if not frames:
        print("警告: 帧列表为空")
        return

    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames:
        # 确保 BGR 格式（OpenCV 默认）
        if frame.shape[2] == 3:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            frame_bgr = frame
        writer.write(frame_bgr)

    writer.release()
    print(f"视频已保存: {output_path}")

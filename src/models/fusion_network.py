"""
NeuroStride-VL: 多模态融合网络
==============================
融合视觉、语言和状态信息的网络
"""

import torch
import torch.nn as nn


class FusionNetwork(nn.Module):
    """
    多模态融合网络

    融合视觉特征、语言特征和机器人状态
    用于高级任务规划和决策
    """

    def __init__(
        self,
        vision_dim: int = 512,
        language_dim: int = 768,
        state_dim: int = 70,
        hidden_dim: int = 256,
        output_dim: int = 23,
    ):
        super().__init__()

        # 视觉特征编码
        self.vision_encoder = nn.Sequential(
            nn.Linear(vision_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # 语言特征编码
        self.language_encoder = nn.Sequential(
            nn.Linear(language_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # 状态特征编码
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # 特征融合
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
        )

        # ��出头
        self.output_head = nn.Linear(hidden_dim, output_dim)

    def forward(
        self,
        vision_features: torch.Tensor,
        language_features: torch.Tensor,
        state_features: torch.Tensor,
    ) -> torch.Tensor:
        """
        前向传播

        Args:
            vision_features: 视觉特征 (batch, vision_dim)
            language_features: 语言特征 (batch, language_dim)
            state_features: 状态特征 (batch, state_dim)

        Returns:
            output: 融合后的输出 (batch, output_dim)
        """
        v = self.vision_encoder(vision_features)
        l = self.language_encoder(language_features)
        s = self.state_encoder(state_features)

        # 拼接
        fused = torch.cat([v, l, s], dim=-1)
        fused = self.fusion(fused)

        output = self.output_head(fused)
        return output


if __name__ == "__main__":
    print("测试 FusionNetwork...")

    batch_size = 16
    model = FusionNetwork()

    vision = torch.randn(batch_size, 512)
    language = torch.randn(batch_size, 768)
    state = torch.randn(batch_size, 70)

    output = model(vision, language, state)
    print(f"输出: {output.shape}")

    print("✅ FusionNetwork 测试通过！")

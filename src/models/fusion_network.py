"""
NeuroStride-VL: Multimodal Fusion Network
=========================================
Fuses vision, language, and state information
"""

import torch
import torch.nn as nn


class FusionNetwork(nn.Module):
    """
    Multimodal fusion network

    Fuses vision features, language features, and robot state
    Used for high-level task planning and decision making
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

        # Vision feature encoder
        self.vision_encoder = nn.Sequential(
            nn.Linear(vision_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Language feature encoder
        self.language_encoder = nn.Sequential(
            nn.Linear(language_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # State feature encoder
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Feature fusion
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
        )

        # Output head
        self.output_head = nn.Linear(hidden_dim, output_dim)

    def forward(
        self,
        vision_features: torch.Tensor,
        language_features: torch.Tensor,
        state_features: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass

        Args:
            vision_features: Vision features (batch, vision_dim)
            language_features: Language features (batch, language_dim)
            state_features: State features (batch, state_dim)

        Returns:
            output: Fused output (batch, output_dim)
        """
        v = self.vision_encoder(vision_features)
        l = self.language_encoder(language_features)
        s = self.state_encoder(state_features)

        # Concatenate
        fused = torch.cat([v, l, s], dim=-1)
        fused = self.fusion(fused)

        output = self.output_head(fused)
        return output


if __name__ == "__main__":
    print("Testing FusionNetwork...")

    batch_size = 16
    model = FusionNetwork()

    vision = torch.randn(batch_size, 512)
    language = torch.randn(batch_size, 768)
    state = torch.randn(batch_size, 70)

    output = model(vision, language, state)
    print(f"Output: {output.shape}")

    print("✅ FusionNetwork test passed!")

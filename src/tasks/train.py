"""Training task orchestrator."""

import os

import hydra
from omegaconf import DictConfig

from ..pipeline.training import TrainingPipeline


@hydra.main(
    version_base=None, config_path="../../configs/training", config_name="default"
)
def train(cfg: DictConfig) -> None:
    """Training task entry point.

    Args:
        cfg: Hydra configuration
    """
    # Set GCS credentials from config
    os.environ["GCS_KEY_ID"] = cfg.GCS_KEY_ID
    os.environ["GCS_SECRET"] = cfg.GCS_SECRET

    # Create and run training pipeline
    pipeline = TrainingPipeline(config=cfg)
    pipeline.run()

    print("\n✓ Training task completed successfully")


if __name__ == "__main__":
    train()

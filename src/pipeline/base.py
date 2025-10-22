"""Base pipeline with MLflow integration."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import mlflow
from omegaconf import DictConfig, OmegaConf


class BasePipeline(ABC):
    """Base pipeline class with built-in MLflow tracking."""

    def __init__(self, config: DictConfig):
        """Initialize pipeline with configuration.

        Args:
            config: Hydra configuration object
        """
        self.config = config
        self.run_id: Optional[str] = None

    def setup_mlflow(self):
        """Set up MLflow tracking."""
        mlflow.set_tracking_uri(self.config.mlflow.tracking_uri)
        mlflow.set_experiment(self.config.mlflow.experiment_name)

    def start_run(self, run_name: Optional[str] = None):
        """Start MLflow run and log config."""
        mlflow.start_run(run_name=run_name)
        self.run_id = mlflow.active_run().info.run_id

        # Log all configuration as parameters
        config_dict = OmegaConf.to_container(self.config, resolve=True)
        self._log_nested_params(config_dict)

    def end_run(self):
        """End MLflow run."""
        mlflow.end_run()
        self.run_id = None

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow.

        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number for tracking over time
        """
        for name, value in metrics.items():
            mlflow.log_metric(name, value, step=step)

    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow.

        Args:
            params: Dictionary of parameter names and values
        """
        mlflow.log_params(params)

    def log_artifacts(self, artifact_path: str):
        """Log artifacts to MLflow.

        Args:
            artifact_path: Path to artifact file or directory
        """
        mlflow.log_artifact(artifact_path)

    def _log_nested_params(self, params: Dict[str, Any], prefix: str = ""):
        """Recursively log nested parameters to MLflow.

        Args:
            params: Dictionary of parameters (can be nested)
            prefix: Prefix for parameter names
        """
        for key, value in params.items():
            param_name = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                self._log_nested_params(value, prefix=f"{param_name}.")
            elif value is not None:
                # MLflow has a limit on param value length
                str_value = str(value)
                if len(str_value) > 250:
                    str_value = str_value[:247] + "..."
                mlflow.log_param(param_name, str_value)

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Execute the pipeline.

        Returns:
            Dictionary containing pipeline results
        """
        pass

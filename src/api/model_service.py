"""Model service for loading and serving predictions."""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import mlflow
import pandas as pd
from catboost import CatBoostClassifier


class ModelService:
    """Service for loading and serving ML models."""

    def __init__(self, model_uri: Optional[str] = None):
        """Initialize model service.

        Args:
            model_uri: MLflow model URI (e.g., 'runs:/run_id/model' or 'models:/model_name/version')
                      If None, will look for MODEL_URI environment variable
        """
        self.model: Optional[CatBoostClassifier] = None
        self.model_version: Optional[str] = None
        self.model_uri = model_uri or os.getenv("MODEL_URI")

        if self.model_uri:
            self.load_model()

    def load_model(self, model_uri: Optional[str] = None) -> None:
        """Load model from MLflow.

        Args:
            model_uri: MLflow model URI. If None, uses instance model_uri
        """
        uri = model_uri or self.model_uri

        if not uri:
            raise ValueError("No model URI provided")

        print(f"Loading model from: {uri}")

        # Load model using MLflow
        self.model = mlflow.catboost.load_model(uri)
        self.model_uri = uri

        # Extract version info
        if uri.startswith("runs:/"):
            self.model_version = uri.split("/")[1][:8]  # First 8 chars of run ID
        elif uri.startswith("models:/"):
            parts = uri.split("/")
            self.model_version = f"{parts[1]}:{parts[2]}"
        else:
            self.model_version = "local"

        print(f"✓ Model loaded (version: {self.model_version})")

    def load_model_from_file(self, model_path: str) -> None:
        """Load model directly from file (for local development).

        Args:
            model_path: Path to saved CatBoost model file
        """
        print(f"Loading model from file: {model_path}")

        self.model = CatBoostClassifier()
        self.model.load_model(model_path)
        self.model_version = Path(model_path).stem

        print("✓ Model loaded from file")

    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Make predictions on features.

        Args:
            features: DataFrame with customer features

        Returns:
            Tuple of (predictions, probabilities)
            - predictions: Binary predictions (0 or 1)
            - probabilities: Probability of churn (class 1)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Make predictions
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)[:, 1]

        return pd.Series(predictions), pd.Series(probabilities)

    def predict_single(self, features: Dict) -> Tuple[bool, float]:
        """Make prediction for a single customer.

        Args:
            features: Dictionary with customer features

        Returns:
            Tuple of (prediction, probability)
        """
        df = pd.DataFrame([features])
        predictions, probabilities = self.predict(df)

        return bool(predictions.iloc[0]), float(probabilities.iloc[0])

    def get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level.

        Args:
            probability: Churn probability (0.0 to 1.0)

        Returns:
            Risk level: "low", "medium", or "high"
        """
        if probability < 0.3:
            return "low"
        elif probability < 0.7:
            return "medium"
        else:
            return "high"

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    def get_version(self) -> Optional[str]:
        """Get current model version."""
        return self.model_version


# Global model service instance
_model_service: Optional[ModelService] = None


def get_model_service() -> ModelService:
    """Get or create global model service instance.

    Returns:
        ModelService instance
    """
    global _model_service

    if _model_service is None:
        _model_service = ModelService()

    return _model_service

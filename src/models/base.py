"""Base model interface following sklearn conventions."""

from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np
import pandas as pd


class BaseModel(ABC):
    """Base class for all models following sklearn interface."""

    def __init__(self, **params):
        """Initialize model with parameters."""
        self.params = params
        self.model = None
        self.feature_names_ = None
        self.categorical_features_ = None

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> "BaseModel":
        """Fit the model.

        Args:
            X: Training features
            y: Training target
            **kwargs: Additional fit parameters (e.g., eval_set)

        Returns:
            Self for chaining
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels.

        Args:
            X: Features to predict

        Returns:
            Predicted class labels
        """
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities.

        Args:
            X: Features to predict

        Returns:
            Predicted probabilities (n_samples, n_classes)
        """
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        pass

    def get_params(self) -> Dict[str, Any]:
        """Get model parameters."""
        return self.params

    def set_params(self, **params) -> "BaseModel":
        """Set model parameters."""
        self.params.update(params)
        return self

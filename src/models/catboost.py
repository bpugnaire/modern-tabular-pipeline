"""CatBoost model implementation."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

from .base import BaseModel


class CatBoostModel(BaseModel):
    """CatBoost classifier wrapper following sklearn interface."""

    def __init__(
        self,
        iterations: int = 100,
        learning_rate: float = 0.1,
        depth: int = 6,
        random_state: int = 42,
        verbose: bool = False,
        **kwargs,
    ):
        """Initialize CatBoost model.

        Args:
            iterations: Number of boosting iterations
            learning_rate: Learning rate
            depth: Tree depth
            random_state: Random seed
            verbose: Whether to print training progress
            **kwargs: Additional CatBoost parameters
        """
        params = {
            "iterations": iterations,
            "learning_rate": learning_rate,
            "depth": depth,
            "random_state": random_state,
            "verbose": verbose,
            **kwargs,
        }
        super().__init__(**params)
        self.model = None

    def _identify_categorical_features(self, X: pd.DataFrame) -> List[str]:
        """Identify categorical features in the dataset."""
        # Only consider object dtype columns as categorical
        # CatBoost can handle numeric columns automatically
        categorical_cols = []
        for col in X.columns:
            if X[col].dtype == "object":
                categorical_cols.append(col)
        return categorical_cols

    def fit(
        self, X: pd.DataFrame, y: pd.Series, eval_set: Optional[tuple] = None, **kwargs
    ) -> "CatBoostModel":
        """Fit CatBoost model.

        Args:
            X: Training features
            y: Training target
            eval_set: Optional (X_val, y_val) for validation
            **kwargs: Additional fit parameters

        Returns:
            Self for chaining
        """
        self.feature_names_ = X.columns.tolist()
        self.categorical_features_ = self._identify_categorical_features(X)

        # Initialize model with categorical features
        self.model = CatBoostClassifier(
            **self.params, cat_features=self.categorical_features_
        )

        # Fit model
        fit_params = {}
        if eval_set is not None:
            fit_params["eval_set"] = eval_set
        fit_params.update(kwargs)

        self.model.fit(X, y, **fit_params)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels."""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names_, importances))

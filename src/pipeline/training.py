"""Training pipeline implementation."""

from typing import Any, Dict, Tuple

import mlflow
import pandas as pd
import polars as pl
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from ..data.loaders import load_features_from_gcs
from ..models.base import BaseModel
from ..models.catboost import CatBoostModel
from .base import BasePipeline


class TrainingPipeline(BasePipeline):
    """Training pipeline with MLflow tracking."""

    def __init__(self, config, model: BaseModel = None):
        """Initialize training pipeline.

        Args:
            config: Hydra configuration
            model: Model instance (if None, creates from config)
        """
        super().__init__(config)
        self.model = model
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def load_data(self) -> pl.DataFrame:
        """Load features from GCS with validation."""
        print(f"Loading features from: {self.config.data.features_path}")
        df = load_features_from_gcs(
            self.config.data.features_path,
            self.config.GCS_KEY_ID,
            self.config.GCS_SECRET,
        )
        print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")
        return df

    def prepare_data(self, df: pl.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target with proper typing.

        Args:
            df: Input Polars dataframe (already validated)

        Returns:
            Tuple of (features, target)
        """
        from ..data.schemas import ChurnFeatureSchema

        target = self.config.model.target
        feature_cols = ChurnFeatureSchema.get_feature_columns()
        categorical_cols = ChurnFeatureSchema.get_categorical_columns()

        # Convert to pandas
        X = df.select(feature_cols).to_pandas()
        y = df.select(target).to_pandas()[target]

        # Ensure proper types: categoricals as string, rest as numeric
        for col in X.columns:
            if col in categorical_cols:
                X[col] = X[col].astype(str)
            elif X[col].dtype == "object":
                # Convert any remaining objects to numeric
                X[col] = pd.to_numeric(X[col], errors="coerce")

        return X, y

    def split_data(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Split data into train/test sets."""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X,
            y,
            test_size=self.config.training.test_size,
            random_state=self.config.training.random_state,
            stratify=y,
        )

        print(f"\nTrain set: {len(self.X_train)} samples")
        print(f"Test set: {len(self.X_test)} samples")

        # After split_data, these are guaranteed to be non-None
        assert self.y_train is not None and self.y_test is not None
        print(
            f"Churn rate - Train: {self.y_train.mean():.2%}, Test: {self.y_test.mean():.2%}"
        )

    def create_model(self) -> BaseModel:
        """Create model from configuration."""
        model_type = self.config.model.type

        if model_type == "catboost":
            model = CatBoostModel(
                iterations=self.config.model.get("iterations", 100),
                learning_rate=self.config.model.get("learning_rate", 0.1),
                depth=self.config.model.get("depth", 6),
                random_state=self.config.training.random_state,
                verbose=self.config.model.get("verbose", False),
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        return model

    def train_model(self):
        """Train the model."""
        if self.model is None:
            self.model = self.create_model()

        print(f"\nTraining {self.config.model.type} model...")

        self.model.fit(
            self.X_train,
            self.y_train,
            eval_set=(self.X_test, self.y_test),
            verbose=20,
        )
        print("✓ Training complete")

    def evaluate_model(self) -> Dict[str, float]:
        """Evaluate model and return metrics."""
        y_pred = self.model.predict(self.X_test)
        y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(self.y_test, y_pred),
            "precision": precision_score(self.y_test, y_pred),
            "recall": recall_score(self.y_test, y_pred),
            "f1": f1_score(self.y_test, y_pred),
            "roc_auc": roc_auc_score(self.y_test, y_pred_proba),
        }

        return metrics

    def log_model_to_mlflow(self):
        """Log trained model to MLflow."""
        if self.config.model.type == "catboost":
            mlflow.catboost.log_model(self.model.model, "model")

        # Log feature importance
        importance = self.model.get_feature_importance()
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]

        print("\nTop 10 Features:")
        for feat, imp in top_features:
            print(f"  {feat:30} {imp:>8.2f}")

    def run(self) -> Dict[str, Any]:
        """Execute the training pipeline.

        Returns:
            Dictionary with metrics and run information
        """
        print("=" * 80)
        print("TRAINING PIPELINE")
        print("=" * 80)

        # Setup MLflow
        self.setup_mlflow()
        self.start_run(run_name="churn_training")

        try:
            # Load and prepare data
            df = self.load_data()
            X, y = self.prepare_data(df)
            self.split_data(X, y)

            # Train model
            self.train_model()

            # Evaluate
            metrics = self.evaluate_model()

            print("\n" + "=" * 80)
            print("RESULTS")
            print("=" * 80)
            for name, value in metrics.items():
                print(f"{name:>15}: {value:.4f}")

            # Log to MLflow
            self.log_metrics(metrics)
            self.log_model_to_mlflow()

            print(f"\n✓ Model saved to MLflow (Run ID: {self.run_id})")

            return {"metrics": metrics, "run_id": self.run_id}

        finally:
            self.end_run()

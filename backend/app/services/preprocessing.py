import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, RobustScaler
from typing import Tuple, List, Optional

class PreprocessingService:
    @staticmethod
    def create_numeric_pipeline(use_robust_scaler: bool = False) -> Pipeline:
        scaler = RobustScaler() if use_robust_scaler else StandardScaler()
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", scaler)
        ])

    @staticmethod
    def prepare_identity_data(
        df: pd.DataFrame,
        feature_cols: List[str]
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Extract features and target while strictly excluding identifier leakage."""
        for col in feature_cols:
            if col not in df.columns:
                raise ValueError(f"Required feature '{col}' missing from dataset.")

        X = df[feature_cols].copy()
        # Ensure correct numeric types
        X = X.apply(pd.to_numeric, errors="coerce")

        y = None
        if "same_identity_label" in df.columns:
            y = df["same_identity_label"].astype(int)

        return X, y

    @staticmethod
    def prepare_anomaly_data(
        df: pd.DataFrame,
        feature_cols: List[str]
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Extract anomaly features strictly excluding labels from features."""
        for col in feature_cols:
            if col not in df.columns:
                raise ValueError(f"Required anomaly feature '{col}' missing from dataset.")

        X = df[feature_cols].copy()
        X = X.apply(pd.to_numeric, errors="coerce")

        y_synthetic = None
        if "synthetic_anomaly_label" in df.columns:
            y_synthetic = df["synthetic_anomaly_label"].astype(int)

        return X, y_synthetic

preprocessing_service = PreprocessingService()

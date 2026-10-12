import numpy as np
import pandas as pd
from typing import Dict, Any, List

IDENTITY_FEATURE_COLUMNS = [
    "same_device_observed",
    "contact_overlap_jaccard",
    "temporal_pattern_similarity",
    "location_overlap_similarity",
    "call_pattern_similarity",
    "shared_case_count",
    "days_between_observations"
]

ANOMALY_FEATURE_COLUMNS = [
    "calls_per_day",
    "unique_contacts_per_day",
    "night_call_ratio",
    "avg_call_duration_seconds",
    "daily_contact_change_ratio",
    "new_cell_count"
]

class FeatureEngineeringService:
    @staticmethod
    def get_identity_feature_columns() -> List[str]:
        return IDENTITY_FEATURE_COLUMNS.copy()

    @staticmethod
    def get_anomaly_feature_columns() -> List[str]:
        return ANOMALY_FEATURE_COLUMNS.copy()

    @staticmethod
    def construct_identity_features_df(records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Constructs an aligned DataFrame from incoming request records."""
        df = pd.DataFrame(records)
        # Ensure all columns exist
        for col in IDENTITY_FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0.0
        return df[IDENTITY_FEATURE_COLUMNS].astype(float)

    @staticmethod
    def construct_anomaly_features_df(records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Constructs an aligned DataFrame from anomaly records."""
        df = pd.DataFrame(records)
        for col in ANOMALY_FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0.0
        return df[ANOMALY_FEATURE_COLUMNS].astype(float)

feature_engineering_service = FeatureEngineeringService()

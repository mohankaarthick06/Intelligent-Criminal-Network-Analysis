import pytest
import pandas as pd
import numpy as np
from backend.app.services.preprocessing import preprocessing_service
from backend.app.services.feature_engineering import feature_engineering_service

def test_preprocessing_numeric_pipeline():
    pipe = preprocessing_service.create_numeric_pipeline()
    data = pd.DataFrame({
        "feat1": [1.0, np.nan, 3.0, 4.0],
        "feat2": [10.0, 20.0, 30.0, np.nan]
    })
    transformed = pipe.fit_transform(data)
    assert transformed.shape == (4, 2)
    assert not np.isnan(transformed).any()

def test_leak_prevention_in_identity_preparation():
    df = pd.DataFrame({
        "record_a": ["SIM1", "SIM2"],
        "record_b": ["SIM3", "SIM4"],
        "same_device_observed": [1, 0],
        "contact_overlap_jaccard": [0.8, 0.1],
        "temporal_pattern_similarity": [0.7, 0.2],
        "location_overlap_similarity": [0.9, 0.3],
        "call_pattern_similarity": [0.85, 0.15],
        "shared_case_count": [2, 0],
        "days_between_observations": [10, 100],
        "same_identity_label": [1, 0]
    })
    cols = feature_engineering_service.get_identity_feature_columns()
    X, y = preprocessing_service.prepare_identity_data(df, cols)
    
    assert "record_a" not in X.columns
    assert "record_b" not in X.columns
    assert "same_identity_label" not in X.columns
    assert y is not None
    assert len(y) == 2

def test_feature_engineering_constructs_aligned_df():
    sample_records = [
        {"contact_overlap_jaccard": 0.5, "call_pattern_similarity": 0.6}
    ]
    df_constructed = feature_engineering_service.construct_identity_features_df(sample_records)
    expected_cols = feature_engineering_service.get_identity_feature_columns()
    assert list(df_constructed.columns) == expected_cols
    assert df_constructed["same_device_observed"].iloc[0] == 0.0 # Default filled
    assert df_constructed["contact_overlap_jaccard"].iloc[0] == 0.5

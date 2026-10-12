import pytest
from backend.app.services.identity_resolution import identity_resolution_service

def test_train_xgboost_identity_model():
    res = identity_resolution_service.train_model(model_type="xgboost", test_size=0.2)
    assert res.model_type == "xgboost"
    assert res.metrics.f1_score >= 0.0
    assert res.metrics.pr_auc >= 0.0
    assert res.metrics.roc_auc >= 0.0
    assert res.metrics.confusion_matrix.tn >= 0
    assert res.metrics.confusion_matrix.tp >= 0
    assert res.metrics.test_size > 0

def test_train_logistic_regression():
    res = identity_resolution_service.train_model(model_type="logistic_regression", test_size=0.2)
    assert res.model_type == "logistic_regression"
    assert res.metrics.f1_score >= 0.0

def test_train_random_forest():
    res = identity_resolution_service.train_model(model_type="random_forest", test_size=0.2)
    assert res.model_type == "random_forest"
    assert res.metrics.f1_score >= 0.0

def test_predict_identity_pair():
    sample_features = {
        "same_device_observed": 1,
        "contact_overlap_jaccard": 0.85,
        "temporal_pattern_similarity": 0.75,
        "location_overlap_similarity": 0.80,
        "call_pattern_similarity": 0.70,
        "shared_case_count": 3,
        "days_between_observations": 15.0
    }
    pred = identity_resolution_service.predict_pair(
        features=sample_features,
        model_type="xgboost",
        pair_id="TEST-PAIR-1"
    )
    assert 0.0 <= pred.probability_same_identity <= 1.0
    assert pred.prediction_label in [0, 1]
    assert pred.pair_id == "TEST-PAIR-1"
    assert "disclaimer" in pred.model_dump()
    assert pred.interpretation is not None

def test_predict_batch():
    batch = [
        {
            "pair_id": "P1",
            "features": {
                "same_device_observed": 0,
                "contact_overlap_jaccard": 0.1,
                "temporal_pattern_similarity": 0.1,
                "location_overlap_similarity": 0.1,
                "call_pattern_similarity": 0.1,
                "shared_case_count": 0,
                "days_between_observations": 200.0
            }
        },
        {
            "pair_id": "P2",
            "features": {
                "same_device_observed": 1,
                "contact_overlap_jaccard": 0.9,
                "temporal_pattern_similarity": 0.9,
                "location_overlap_similarity": 0.9,
                "call_pattern_similarity": 0.9,
                "shared_case_count": 5,
                "days_between_observations": 5.0
            }
        }
    ]
    preds = identity_resolution_service.predict_batch(batch, model_type="xgboost")
    assert len(preds) == 2
    assert preds[0].probability_same_identity <= preds[1].probability_same_identity

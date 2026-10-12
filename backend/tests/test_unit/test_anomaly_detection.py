import pytest
from backend.app.services.anomaly_detection import anomaly_detection_service

def test_train_anomaly_model():
    res = anomaly_detection_service.train_model(contamination=0.09)
    assert res.total_samples > 0
    assert res.anomalies_detected > 0
    assert res.anomaly_rate > 0.0
    if res.evaluation_metrics:
        assert res.evaluation_metrics["f1_score"] >= 0.0
        assert res.evaluation_metrics["precision"] >= 0.0

def test_detect_anomalies():
    items = [
        {
            "entity_id": "NORM-1",
            "calls_per_day": 5.0,
            "unique_contacts_per_day": 3.0,
            "night_call_ratio": 0.05,
            "avg_call_duration_seconds": 60.0,
            "daily_contact_change_ratio": 0.1,
            "new_cell_count": 1
        },
        {
            "entity_id": "SUSP-1",
            "calls_per_day": 95.0,
            "unique_contacts_per_day": 60.0,
            "night_call_ratio": 0.90,
            "avg_call_duration_seconds": 350.0,
            "daily_contact_change_ratio": 0.95,
            "new_cell_count": 15
        }
    ]
    detection = anomaly_detection_service.detect(items)
    assert detection.total_checked == 2
    # Verify suspicious entity is scored more anomalous than normal entity
    susp_score = detection.results[1].anomaly_score
    norm_score = detection.results[0].anomaly_score
    # In Isolation Forest decision_function, lower score means more anomalous
    assert susp_score < norm_score

def test_anomaly_summary():
    summary = anomaly_detection_service.get_summary()
    assert summary.total_entities > 0
    assert summary.anomalies_count > 0
    assert len(summary.top_anomalies) > 0
    assert "calls_per_day" in summary.feature_averages_normal

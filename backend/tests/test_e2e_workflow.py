import pytest

def test_full_end_to_end_investigative_workflow(client):
    """
    Simulates a complete analytical investigation session from start to finish:
    1. Health check & system diagnostics
    2. Data validation on raw CDR & Identity pairs
    3. Train Identity Resolution models (XGBoost, RF, LR)
    4. Predict candidate burner SIM match (high overlap)
    5. Predict candidate burner SIM non-match (low overlap)
    6. Batch prediction
    7. Train & evaluate Isolation Forest anomaly detection
    8. Detect an anomalous subscriber feature vector
    9. Construct CDR communication graph and detect Louvain communities
    10. Perform Link Analysis between 2 nodes
    11. Fetch evaluation summary comparison
    12. Verify error handling for invalid payloads and missing datasets
    """
    # 1. Health check
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["ready"] is True

    # 2. Data validation
    ds_val = client.post("/api/v1/datasets/cdr/validate")
    assert ds_val.status_code == 200
    assert ds_val.json()["is_valid"] is True

    ds_qual = client.get("/api/v1/datasets/identity_resolution_pairs/quality")
    assert ds_qual.status_code == 200
    assert ds_qual.json()["integrity_score"] > 85.0

    # 3. Train Identity Models
    for mtype in ["xgboost", "random_forest", "logistic_regression"]:
        train_res = client.post("/api/v1/identity/train", json={"model_type": mtype, "test_size": 0.2})
        assert train_res.status_code == 200
        data = train_res.json()
        assert data["model_type"] == mtype
        assert data["metrics"]["f1_score"] >= 0.0

    # 4. Predict high similarity candidate pair
    match_res = client.post("/api/v1/identity/predict", json={
        "model_type": "xgboost",
        "pair_id": "PAIR-HIGH-CONF",
        "features": {
            "same_device_observed": 1,
            "contact_overlap_jaccard": 0.95,
            "temporal_pattern_similarity": 0.88,
            "location_overlap_similarity": 0.82,
            "call_pattern_similarity": 0.91,
            "shared_case_count": 4,
            "days_between_observations": 5.0
        }
    })
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["probability_same_identity"] >= 0.5
    assert match_data["prediction_label"] == 1

    # 5. Predict low similarity pair
    non_match_res = client.post("/api/v1/identity/predict", json={
        "model_type": "xgboost",
        "pair_id": "PAIR-LOW-CONF",
        "features": {
            "same_device_observed": 0,
            "contact_overlap_jaccard": 0.02,
            "temporal_pattern_similarity": 0.05,
            "location_overlap_similarity": 0.01,
            "call_pattern_similarity": 0.04,
            "shared_case_count": 0,
            "days_between_observations": 250.0
        }
    })
    assert non_match_res.status_code == 200
    non_match_data = non_match_res.json()
    assert non_match_data["probability_same_identity"] < 0.5
    assert non_match_data["prediction_label"] == 0

    # 6. Batch prediction
    batch_res = client.post("/api/v1/identity/predict/batch", json={
        "model_type": "xgboost",
        "items": [
            {
                "pair_id": "P1",
                "features": {
                    "same_device_observed": 1,
                    "contact_overlap_jaccard": 0.85,
                    "temporal_pattern_similarity": 0.85,
                    "location_overlap_similarity": 0.85,
                    "call_pattern_similarity": 0.85,
                    "shared_case_count": 2,
                    "days_between_observations": 10.0
                }
            },
            {
                "pair_id": "P2",
                "features": {
                    "same_device_observed": 0,
                    "contact_overlap_jaccard": 0.05,
                    "temporal_pattern_similarity": 0.05,
                    "location_overlap_similarity": 0.05,
                    "call_pattern_similarity": 0.05,
                    "shared_case_count": 0,
                    "days_between_observations": 100.0
                }
            }
        ]
    })
    assert batch_res.status_code == 200
    assert batch_res.json()["total_items"] == 2

    # 7. Anomaly model training
    anom_train = client.post("/api/v1/anomalies/train", json={"contamination": 0.09})
    assert anom_train.status_code == 200
    assert anom_train.json()["anomalies_detected"] > 0

    # 8. Anomaly detection
    anom_det = client.post("/api/v1/anomalies/detect", json={
        "items": [
            {
                "entity_id": "OUTLIER-1",
                "calls_per_day": 88.0,
                "unique_contacts_per_day": 62.0,
                "night_call_ratio": 0.92,
                "avg_call_duration_seconds": 310.0,
                "daily_contact_change_ratio": 0.89,
                "new_cell_count": 12
            }
        ]
    })
    assert anom_det.status_code == 200
    assert anom_det.json()["total_checked"] == 1
    assert anom_det.json()["results"][0]["is_anomaly"] is True

    # 9. Graph construction
    graph_res = client.post("/api/v1/graph/build", json={"min_interactions": 1, "max_nodes": 100})
    assert graph_res.status_code == 200
    gdata = graph_res.json()
    assert gdata["summary"]["node_count"] > 0
    assert gdata["summary"]["community_count"] > 0

    # 10. Link Analysis
    nodes = [n["id"] for n in gdata["nodes"][:2]]
    if len(nodes) == 2:
        link_res = client.post("/api/v1/graph/link-analysis", json={
            "source_node": nodes[0],
            "target_node": nodes[1]
        })
        assert link_res.status_code == 200
        assert "jaccard_coefficient" in link_res.json()

    # 11. Model evaluation summary
    eval_sum = client.get("/api/v1/evaluation/summary")
    assert eval_sum.status_code == 200
    assert len(eval_sum.json()["identity_models"]) >= 3

    # 12. Error handling checks
    bad_ds = client.get("/api/v1/datasets/nonexistent/summary")
    assert bad_ds.status_code == 404

    bad_predict = client.post("/api/v1/identity/predict", json={})
    assert bad_predict.status_code == 422

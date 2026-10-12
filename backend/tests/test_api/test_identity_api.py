def test_train_and_predict_identity(client):
    # 1. Train model
    train_res = client.post("/api/v1/identity/train", json={
        "model_type": "xgboost",
        "test_size": 0.2,
        "random_seed": 42
    })
    assert train_res.status_code == 200
    train_data = train_res.json()
    assert train_data["model_type"] == "xgboost"
    assert "metrics" in train_data

    # 2. Predict single pair
    predict_res = client.post("/api/v1/identity/predict", json={
        "model_type": "xgboost",
        "pair_id": "PAIR-101",
        "features": {
            "same_device_observed": 1,
            "contact_overlap_jaccard": 0.88,
            "temporal_pattern_similarity": 0.72,
            "location_overlap_similarity": 0.65,
            "call_pattern_similarity": 0.81,
            "shared_case_count": 2,
            "days_between_observations": 12.0
        }
    })
    assert predict_res.status_code == 200
    pred_data = predict_res.json()
    assert 0.0 <= pred_data["probability_same_identity"] <= 1.0
    assert pred_data["prediction_label"] in [0, 1]
    assert "disclaimer" in pred_data

    # 3. Batch predict
    batch_res = client.post("/api/v1/identity/predict/batch", json={
        "model_type": "xgboost",
        "items": [
            {
                "pair_id": "P-1",
                "features": {
                    "same_device_observed": 0,
                    "contact_overlap_jaccard": 0.1,
                    "temporal_pattern_similarity": 0.1,
                    "location_overlap_similarity": 0.1,
                    "call_pattern_similarity": 0.1,
                    "shared_case_count": 0,
                    "days_between_observations": 150.0
                }
            }
        ]
    })
    assert batch_res.status_code == 200
    batch_data = batch_res.json()
    assert batch_data["total_items"] == 1
    assert len(batch_data["predictions"]) == 1

def test_list_identity_models(client):
    res = client.get("/api/v1/identity/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data

def test_invalid_predict_request(client):
    # Missing required features
    res = client.post("/api/v1/identity/predict", json={
        "features": {
            "same_device_observed": 1
            # Missing other required features
        }
    })
    assert res.status_code == 422

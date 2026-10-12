def test_anomaly_workflow(client):
    # 1. Train
    train_res = client.post("/api/v1/anomalies/train", json={"contamination": 0.09})
    assert train_res.status_code == 200
    train_data = train_res.json()
    assert train_data["anomalies_detected"] > 0

    # 2. Summary
    sum_res = client.get("/api/v1/anomalies/summary")
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["total_entities"] > 0
    assert len(sum_data["top_anomalies"]) > 0

    # 3. Detect
    detect_res = client.post("/api/v1/anomalies/detect", json={
        "items": [
            {
                "entity_id": "TEST-ENT-1",
                "calls_per_day": 85.0,
                "unique_contacts_per_day": 50.0,
                "night_call_ratio": 0.85,
                "avg_call_duration_seconds": 220.0,
                "daily_contact_change_ratio": 0.8,
                "new_cell_count": 9
            }
        ]
    })
    assert detect_res.status_code == 200
    detect_data = detect_res.json()
    assert detect_data["total_checked"] == 1
    assert len(detect_data["results"]) == 1
    assert "risk_level" in detect_data["results"][0]

def test_get_anomaly_evaluation(client):
    res = client.get("/api/v1/anomalies/evaluation")
    assert res.status_code == 200

def test_list_datasets(client):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert isinstance(datasets, list)
    assert "cdr" in datasets
    assert "identity_resolution_pairs" in datasets

def test_dataset_summary(client):
    response = client.get("/api/v1/datasets/cdr/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "cdr"
    assert data["row_count"] == 5000
    assert len(data["columns"]) == 16
    assert len(data["column_details"]) == 16
    assert len(data["preview"]) <= 10

def test_dataset_validate(client):
    response = client.post("/api/v1/datasets/identity_resolution_pairs/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["total_checks"] > 0

def test_dataset_quality(client):
    response = client.get("/api/v1/datasets/behavior_anomaly_features/quality")
    assert response.status_code == 200
    data = response.json()
    assert data["integrity_score"] > 80.0
    assert isinstance(data["recommendations"], list)

def test_dataset_not_found(client):
    response = client.get("/api/v1/datasets/unknown_nonexistent_dataset/summary")
    assert response.status_code == 404

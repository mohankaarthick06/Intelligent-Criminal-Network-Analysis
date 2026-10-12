def test_evaluation_summary(client):
    res = client.get("/api/v1/evaluation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "generated_at" in data
    assert "comparative_analysis" in data

def test_artifacts_status(client):
    res = client.get("/api/v1/artifacts/status")
    assert res.status_code == 200
    data = res.json()
    assert "models_directory" in data
    assert "reports_directory" in data

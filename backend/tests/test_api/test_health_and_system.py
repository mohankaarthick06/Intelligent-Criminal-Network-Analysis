def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["datasets_loaded"] is True

def test_system_info_endpoint(client):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert len(data["datasets_available"]) > 0

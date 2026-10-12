def test_build_and_query_graph(client):
    # 1. Build
    build_res = client.post("/api/v1/graph/build", json={
        "min_interactions": 1,
        "max_nodes": 50
    })
    assert build_res.status_code == 200
    data = build_res.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["summary"]["node_count"] > 0

    # 2. Summary
    sum_res = client.get("/api/v1/graph/summary?min_interactions=1")
    assert sum_res.status_code == 200
    assert sum_res.json()["node_count"] > 0

    # 3. Nodes
    nodes_res = client.get("/api/v1/graph/nodes?limit=10&offset=0")
    assert nodes_res.status_code == 200
    assert len(nodes_res.json()) <= 10

    # 4. Edges
    edges_res = client.get("/api/v1/graph/edges?limit=10&offset=0")
    assert edges_res.status_code == 200
    assert len(edges_res.json()) <= 10

    # 5. Communities
    comm_res = client.get("/api/v1/graph/communities?min_interactions=1")
    assert comm_res.status_code == 200
    assert len(comm_res.json()) > 0

    # 6. Centrality
    cent_res = client.get("/api/v1/graph/centrality?algorithm=degree&top_k=5")
    assert cent_res.status_code == 200
    assert len(cent_res.json()) <= 5

    # 7. Link analysis
    link_res = client.post("/api/v1/graph/link-analysis", json={
        "source_node": "P0001",
        "target_node": "P0002"
    })
    assert link_res.status_code == 200
    link_data = link_res.json()
    assert "jaccard_coefficient" in link_data

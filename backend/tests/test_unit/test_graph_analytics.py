import pytest
import networkx as nx
from backend.app.services.graph_analytics import graph_analytics_service

def test_graph_algorithms_on_known_small_structure():
    """Verify centrality, common neighbors, and Jaccard on known 4-node kite graph."""
    # A - B, B - C, C - A (triangle), and C - D (tail)
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")])

    # 1. Degree Centrality
    # Deg(A) = 2/3, Deg(B) = 2/3, Deg(C) = 3/3 = 1.0, Deg(D) = 1/3
    deg_cent = nx.degree_centrality(G)
    assert deg_cent["C"] == 1.0
    assert deg_cent["D"] == 1.0 / 3.0

    # 2. Common Neighbors
    common_ab = list(nx.common_neighbors(G, "A", "B"))
    assert common_ab == ["C"]

    # 3. Jaccard Coefficient
    # N(A) = {B, C}, N(B) = {A, C}. Intersection={C} (size 1), Union={A, B, C} (size 3) => 1/3
    jaccard_ab = list(nx.jaccard_coefficient(G, [("A", "B")]))[0][2]
    assert pytest.approx(jaccard_ab, 0.01) == 1.0 / 3.0

    # 4. Shortest path
    assert nx.shortest_path(G, "A", "D") == ["A", "C", "D"]
    assert nx.shortest_path_length(G, "A", "D") == 2

def test_build_network_from_cdr():
    G = graph_analytics_service.build_network_graph(min_interactions=1)
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0

def test_graph_data_response():
    data = graph_analytics_service.get_graph_data(min_interactions=1, max_nodes=50)
    assert len(data.nodes) <= 50
    assert data.summary.node_count > 0
    assert data.summary.edge_count > 0
    assert data.summary.density >= 0.0

def test_link_analysis_existing_and_nonexistent_nodes():
    # Nonexistent nodes
    res_none = graph_analytics_service.analyze_link("NONEXISTENT_1", "NONEXISTENT_2")
    assert res_none.direct_edge_exists is False
    assert res_none.shortest_path_distance is None

    # Real nodes from graph
    G = graph_analytics_service.build_network_graph()
    nodes = list(G.nodes())
    if len(nodes) >= 2:
        u, v = nodes[0], nodes[1]
        res = graph_analytics_service.analyze_link(u, v)
        assert res.source_node == u
        assert res.target_node == v
        assert res.jaccard_coefficient >= 0.0

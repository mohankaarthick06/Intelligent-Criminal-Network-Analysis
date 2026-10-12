import math
import networkx as nx
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Set
from ..core.config import settings
from ..core.logging_config import logger
from ..repositories.dataset_repository import dataset_repository
from ..schemas.graph import (
    GraphNode, GraphEdge, GraphSummaryResponse,
    GraphDataResponse, CommunityResponse, CentralityResponse,
    LinkAnalysisResponse
)

class GraphAnalyticsService:
    def __init__(self):
        self._cached_graph: Optional[nx.Graph] = None
        self._cached_filter_key: Optional[str] = None

    def build_network_graph(
        self,
        min_interactions: int = 1,
        case_id: Optional[str] = None,
        city: Optional[str] = None,
        call_type: Optional[str] = None
    ) -> nx.Graph:
        """Constructs an undirected weighted network graph from cdr.csv."""
        df = dataset_repository.load_dataset("cdr")

        # Apply filters
        if case_id:
            df = df[df["case_id"] == case_id]
        if city:
            df = df[df["cell_city"].str.lower() == city.lower()]
        if call_type:
            df = df[df["call_type"].str.lower() == call_type.lower()]

        G = nx.Graph()

        if len(df) == 0:
            return G

        # Track node metadata
        node_cities: Dict[str, str] = {}
        node_phones: Dict[str, str] = {}
        edge_data: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for _, row in df.iterrows():
            u = str(row["caller_person_id"])
            v = str(row["receiver_person_id"])
            if u == v:
                continue # ignore self-loops in primary communication graph

            edge_key = (min(u, v), max(u, v))
            duration = int(row.get("call_duration_seconds", 0))
            ctype = str(row.get("call_type", "voice"))

            if edge_key not in edge_data:
                edge_data[edge_key] = {
                    "weight": 1,
                    "total_duration_sec": duration,
                    "call_types": {ctype}
                }
            else:
                edge_data[edge_key]["weight"] += 1
                edge_data[edge_key]["total_duration_sec"] += duration
                edge_data[edge_key]["call_types"].add(ctype)

            # Metadata
            if "cell_city" in row and pd.notna(row["cell_city"]):
                node_cities[u] = str(row["cell_city"])
            if "caller_number" in row and pd.notna(row["caller_number"]):
                node_phones[u] = str(row["caller_number"])
            if "receiver_number" in row and pd.notna(row["receiver_number"]):
                node_phones[v] = str(row["receiver_number"])

        for (u, v), data in edge_data.items():
            if data["weight"] >= min_interactions:
                G.add_edge(
                    u, v,
                    weight=data["weight"],
                    total_duration_sec=data["total_duration_sec"],
                    call_types=list(data["call_types"])
                )

        # Assign node attributes
        for n in G.nodes():
            G.nodes[n]["city"] = node_cities.get(n, "Unknown")
            G.nodes[n]["phone"] = node_phones.get(n, "N/A")

        return G

    def get_graph_data(
        self,
        min_interactions: int = 1,
        case_id: Optional[str] = None,
        city: Optional[str] = None,
        call_type: Optional[str] = None,
        max_nodes: int = 500
    ) -> GraphDataResponse:
        G = self.build_network_graph(
            min_interactions=min_interactions,
            case_id=case_id,
            city=city,
            call_type=call_type
        )

        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()

        if node_count == 0:
            summary = GraphSummaryResponse(
                node_count=0,
                edge_count=0,
                density=0.0,
                connected_components=0,
                community_count=0,
                max_degree=0,
                avg_degree=0.0,
                top_central_nodes=[],
                filters_applied={
                    "min_interactions": min_interactions,
                    "case_id": case_id,
                    "city": city,
                    "call_type": call_type
                }
            )
            return GraphDataResponse(nodes=[], edges=[], summary=summary)

        # Degree centrality
        deg_centrality = nx.degree_centrality(G)

        # Betweenness centrality (use k approximation if graph is large)
        k_val = min(100, node_count) if node_count > 100 else None
        bet_centrality = nx.betweenness_centrality(G, k=k_val, seed=settings.RANDOM_SEED)

        # Louvain communities
        communities = {}
        try:
            louvain_sets = nx.community.louvain_communities(G, seed=settings.RANDOM_SEED)
            for c_idx, c_nodes in enumerate(louvain_sets):
                for node in c_nodes:
                    communities[node] = c_idx
        except Exception as e:
            logger.warning(f"Louvain failed: {e}. Fallback to component index.")
            for c_idx, c_nodes in enumerate(nx.connected_components(G)):
                for node in c_nodes:
                    communities[node] = c_idx

        # Select top nodes if graph exceeds max_nodes
        if node_count > max_nodes:
            top_nodes = sorted(G.nodes(), key=lambda n: G.degree[n], reverse=True)[:max_nodes]
            subG = G.subgraph(top_nodes).copy()
        else:
            subG = G

        # Build node schemas
        nodes: List[GraphNode] = []
        for n in subG.nodes():
            deg = G.degree[n]
            nodes.append(GraphNode(
                id=n,
                label=f"{n} ({G.nodes[n].get('city', 'Unknown')})",
                entity_type="person",
                degree=deg,
                degree_centrality=round(deg_centrality.get(n, 0.0), 4),
                betweenness_centrality=round(bet_centrality.get(n, 0.0), 4),
                community=communities.get(n, 0),
                city=G.nodes[n].get("city", "Unknown"),
                total_calls=deg,
                phone_number=G.nodes[n].get("phone", "N/A")
            ))

        # Build edge schemas
        edges: List[GraphEdge] = []
        for u, v, data in subG.edges(data=True):
            edges.append(GraphEdge(
                id=f"{u}-{v}",
                source=u,
                target=v,
                weight=int(data.get("weight", 1)),
                total_duration_sec=int(data.get("total_duration_sec", 0)),
                call_types=list(data.get("call_types", ["voice"]))
            ))

        # Top central nodes for summary
        sorted_central = sorted(deg_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        top_central = [{"node": n, "degree_centrality": round(c, 4), "degree": G.degree[n]} for n, c in sorted_central]

        degrees = [d for _, d in G.degree()]
        summary = GraphSummaryResponse(
            node_count=node_count,
            edge_count=edge_count,
            density=round(float(nx.density(G)), 4),
            connected_components=nx.number_connected_components(G),
            community_count=len(set(communities.values())) if communities else 0,
            max_degree=max(degrees) if degrees else 0,
            avg_degree=round(float(sum(degrees) / max(1, len(degrees))), 2),
            top_central_nodes=top_central,
            filters_applied={
                "min_interactions": min_interactions,
                "case_id": case_id,
                "city": city,
                "call_type": call_type,
                "returned_nodes": len(nodes),
                "returned_edges": len(edges)
            }
        )

        return GraphDataResponse(nodes=nodes, edges=edges, summary=summary)

    def analyze_link(self, source_node: str, target_node: str) -> LinkAnalysisResponse:
        G = self.build_network_graph()

        if source_node not in G or target_node not in G:
            return LinkAnalysisResponse(
                source_node=source_node,
                target_node=target_node,
                common_neighbors=[],
                common_neighbors_count=0,
                jaccard_coefficient=0.0,
                adamic_adar_index=0.0,
                direct_edge_exists=False,
                shortest_path_distance=None,
                shortest_path=None
            )

        common_nbrs = sorted(list(nx.common_neighbors(G, source_node, target_node)))
        common_count = len(common_nbrs)

        # Jaccard coefficient
        jaccard_preds = list(nx.jaccard_coefficient(G, [(source_node, target_node)]))
        jaccard_val = float(round(jaccard_preds[0][2], 4)) if jaccard_preds else 0.0

        # Adamic-Adar index
        aa_val = 0.0
        try:
            aa_preds = list(nx.adamic_adar_index(G, [(source_node, target_node)]))
            aa_val = float(round(aa_preds[0][2], 4)) if aa_preds else 0.0
        except Exception:
            aa_val = 0.0

        direct_edge = G.has_edge(source_node, target_node)

        dist = None
        path = None
        try:
            if nx.has_path(G, source_node, target_node):
                path = nx.shortest_path(G, source_node, target_node)
                dist = len(path) - 1
        except Exception:
            pass

        return LinkAnalysisResponse(
            source_node=source_node,
            target_node=target_node,
            common_neighbors=common_nbrs,
            common_neighbors_count=common_count,
            jaccard_coefficient=jaccard_val,
            adamic_adar_index=aa_val,
            direct_edge_exists=direct_edge,
            shortest_path_distance=dist,
            shortest_path=path
        )

graph_analytics_service = GraphAnalyticsService()

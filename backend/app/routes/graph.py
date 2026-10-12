from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from ..schemas.graph import (
    GraphBuildRequest, GraphDataResponse, GraphSummaryResponse,
    GraphNode, GraphEdge, CommunityResponse, CentralityResponse,
    LinkAnalysisRequest, LinkAnalysisResponse
)
from ..services.graph_analytics import graph_analytics_service

router = APIRouter(prefix="/api/v1/graph", tags=["Graph Analytics"])

@router.post("/build", response_model=GraphDataResponse)
def build_graph(req: GraphBuildRequest):
    return graph_analytics_service.get_graph_data(
        min_interactions=req.min_interactions,
        case_id=req.case_id,
        city=req.city,
        call_type=req.call_type,
        max_nodes=req.max_nodes
    )

@router.get("/summary", response_model=GraphSummaryResponse)
def get_graph_summary(
    min_interactions: int = Query(1, ge=1),
    case_id: Optional[str] = None,
    city: Optional[str] = None,
    call_type: Optional[str] = None
):
    graph_data = graph_analytics_service.get_graph_data(
        min_interactions=min_interactions,
        case_id=case_id,
        city=city,
        call_type=call_type,
        max_nodes=1000
    )
    return graph_data.summary

@router.get("/nodes", response_model=List[GraphNode])
def get_graph_nodes(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    min_interactions: int = Query(1, ge=1)
):
    graph_data = graph_analytics_service.get_graph_data(min_interactions=min_interactions, max_nodes=1000)
    return graph_data.nodes[offset : offset + limit]

@router.get("/edges", response_model=List[GraphEdge])
def get_graph_edges(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    min_interactions: int = Query(1, ge=1)
):
    graph_data = graph_analytics_service.get_graph_data(min_interactions=min_interactions, max_nodes=1000)
    return graph_data.edges[offset : offset + limit]

@router.get("/communities", response_model=List[CommunityResponse])
def get_graph_communities(min_interactions: int = Query(1, ge=1)):
    graph_data = graph_analytics_service.get_graph_data(min_interactions=min_interactions, max_nodes=1000)
    comm_map: Dict[int, List[str]] = {}
    for node in graph_data.nodes:
        comm_map.setdefault(node.community, []).append(node.id)

    res = []
    for cid, members in sorted(comm_map.items()):
        res.append(CommunityResponse(
            community_id=cid,
            size=len(members),
            members=members,
            representative_node=members[0] if members else "None"
        ))
    return res

@router.get("/centrality", response_model=List[Dict[str, Any]])
def get_graph_centrality(
    algorithm: str = Query("degree", description="'degree' or 'betweenness'"),
    top_k: int = Query(20, ge=1, le=100)
):
    graph_data = graph_analytics_service.get_graph_data(min_interactions=1, max_nodes=1000)
    if algorithm.lower() == "betweenness":
        nodes_sorted = sorted(graph_data.nodes, key=lambda n: n.betweenness_centrality, reverse=True)[:top_k]
        return [{"node": n.id, "score": n.betweenness_centrality, "city": n.city} for n in nodes_sorted]
    else:
        nodes_sorted = sorted(graph_data.nodes, key=lambda n: n.degree_centrality, reverse=True)[:top_k]
        return [{"node": n.id, "score": n.degree_centrality, "degree": n.degree, "city": n.city} for n in nodes_sorted]

@router.post("/link-analysis", response_model=LinkAnalysisResponse)
def analyze_link(req: LinkAnalysisRequest):
    return graph_analytics_service.analyze_link(req.source_node, req.target_node)

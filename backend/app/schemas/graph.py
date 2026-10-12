from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class GraphBuildRequest(BaseModel):
    min_interactions: int = Field(1, ge=1, description="Minimum call interactions to form an edge")
    case_id: Optional[str] = Field(None, description="Filter by case ID")
    city: Optional[str] = Field(None, description="Filter by cell city")
    call_type: Optional[str] = Field(None, description="Filter by call type: voice, sms")
    max_nodes: int = Field(500, ge=10, le=2000, description="Max nodes to return for graph visualization")

class GraphNode(BaseModel):
    id: str
    label: str
    entity_type: str = "person"
    degree: int
    degree_centrality: float
    betweenness_centrality: float
    community: int
    city: Optional[str] = None
    total_calls: int = 0
    phone_number: Optional[str] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    weight: int # count of interactions
    total_duration_sec: int
    call_types: List[str]

class GraphSummaryResponse(BaseModel):
    node_count: int
    edge_count: int
    density: float
    connected_components: int
    community_count: int
    max_degree: int
    avg_degree: float
    top_central_nodes: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]

class GraphDataResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    summary: GraphSummaryResponse

class CommunityResponse(BaseModel):
    community_id: int
    size: int
    members: List[str]
    representative_node: str

class CentralityResponse(BaseModel):
    algorithm: str
    scores: List[Dict[str, Any]]

class LinkAnalysisRequest(BaseModel):
    source_node: str
    target_node: str

class LinkAnalysisResponse(BaseModel):
    source_node: str
    target_node: str
    common_neighbors: List[str]
    common_neighbors_count: int
    jaccard_coefficient: float
    adamic_adar_index: float
    direct_edge_exists: bool
    shortest_path_distance: Optional[int] = None
    shortest_path: Optional[List[str]] = None

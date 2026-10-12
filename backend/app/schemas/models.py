from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ModelMetadata(BaseModel):
    model_name: str
    task: str # identity_resolution or anomaly_detection
    algorithm: str
    version: str
    trained_at: str
    artifact_path: str
    is_active: bool
    evaluation_metrics: Optional[Dict[str, Any]] = None

class ModelListResponse(BaseModel):
    models: List[ModelMetadata]
    active_identity_model: Optional[str] = None
    active_anomaly_model: Optional[str] = None

class EvaluationSummaryResponse(BaseModel):
    generated_at: str
    identity_models: List[Dict[str, Any]]
    best_identity_model: Optional[str] = None
    anomaly_model: Optional[Dict[str, Any]] = None
    comparative_analysis: str

class ArtifactStatusResponse(BaseModel):
    models_directory: str
    reports_directory: str
    saved_models_count: int
    saved_reports_count: int
    models: List[str]
    reports: List[str]

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    app_name: str

class ReadinessResponse(BaseModel):
    ready: bool = True
    datasets_loaded: bool
    models_ready: bool
    details: Dict[str, Any] = Field(default_factory=dict)

class SystemInfoResponse(BaseModel):
    app_name: str
    version: str
    environment: str = "local"
    python_version: str
    datasets_available: list[str]
    available_models: list[str]

import sys
from fastapi import APIRouter
from ..core.config import settings
from ..schemas.common import HealthResponse, ReadinessResponse, SystemInfoResponse
from ..repositories.dataset_repository import dataset_repository
from ..repositories.artifact_repository import artifact_repository

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        app_name=settings.APP_NAME
    )

@router.get("/ready", response_model=ReadinessResponse)
def get_readiness():
    datasets = dataset_repository.list_datasets()
    models = artifact_repository.list_models()
    return ReadinessResponse(
        ready=len(datasets) > 0,
        datasets_loaded=len(datasets) > 0,
        models_ready=len(models) > 0,
        details={
            "datasets_found": len(datasets),
            "models_saved": len(models)
        }
    )

@router.get("/api/v1/system/info", response_model=SystemInfoResponse)
def get_system_info():
    return SystemInfoResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment="local",
        python_version=sys.version.split()[0],
        datasets_available=dataset_repository.list_datasets(),
        available_models=artifact_repository.list_models()
    )

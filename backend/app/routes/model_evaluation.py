from fastapi import APIRouter
from typing import Dict, Any, List
from ..schemas.models import EvaluationSummaryResponse, ArtifactStatusResponse
from ..services.model_evaluation import model_evaluation_service
from ..repositories.artifact_repository import artifact_repository

router = APIRouter(tags=["Model Evaluation & Artifacts"])

@router.get("/api/v1/evaluation/summary", response_model=EvaluationSummaryResponse)
def get_evaluation_summary():
    return model_evaluation_service.get_summary()

@router.get("/api/v1/evaluation/models")
def get_evaluation_models():
    return artifact_repository.list_models()

@router.get("/api/v1/artifacts/status", response_model=ArtifactStatusResponse)
def get_artifact_status():
    models = artifact_repository.list_models()
    reports = artifact_repository.list_reports()
    return ArtifactStatusResponse(
        models_directory=str(artifact_repository.models_dir),
        reports_directory=str(artifact_repository.reports_dir),
        saved_models_count=len(models),
        saved_reports_count=len(reports),
        models=models,
        reports=reports
    )

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas.anomalies import (
    AnomalyTrainRequest, AnomalyTrainResponse,
    AnomalyDetectRequest, AnomalyDetectResponse,
    AnomalySummaryResponse
)
from ..services.anomaly_detection import anomaly_detection_service
from ..repositories.artifact_repository import artifact_repository

router = APIRouter(prefix="/api/v1/anomalies", tags=["Anomaly Detection"])

@router.post("/train", response_model=AnomalyTrainResponse)
def train_anomaly_model(req: AnomalyTrainRequest):
    return anomaly_detection_service.train_model(
        contamination=req.contamination,
        random_seed=req.random_seed,
        evaluate=req.evaluate_against_synthetic_labels
    )

@router.post("/detect", response_model=AnomalyDetectResponse)
def detect_anomalies(req: AnomalyDetectRequest):
    if len(req.items) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000 items.")
    items_dict = [i.model_dump() for i in req.items]
    return anomaly_detection_service.detect(items_dict)

@router.get("/summary", response_model=AnomalySummaryResponse)
def get_anomaly_summary():
    return anomaly_detection_service.get_summary()

@router.get("/evaluation")
def get_anomaly_evaluation():
    rep = artifact_repository.load_report("anomaly_evaluation")
    if not rep:
        if artifact_repository.model_exists("behavior_isolation_forest"):
            bundle = artifact_repository.load_model("behavior_isolation_forest")
            return bundle.get("evaluation_metrics", {})
        raise HTTPException(status_code=404, detail="No evaluation found. Train the anomaly model first.")
    return rep

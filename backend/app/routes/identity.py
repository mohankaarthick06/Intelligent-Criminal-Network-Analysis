from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from ..schemas.identity import (
    IdentityTrainRequest, IdentityTrainResponse,
    IdentityPredictRequest, IdentityPredictResponse,
    BatchIdentityPredictRequest, BatchIdentityPredictResponse,
    ModelEvaluationMetrics
)
from ..schemas.models import ModelListResponse, ModelMetadata
from ..services.identity_resolution import identity_resolution_service
from ..repositories.artifact_repository import artifact_repository

router = APIRouter(prefix="/api/v1/identity", tags=["Identity Resolution"])

@router.get("/models", response_model=ModelListResponse)
def list_identity_models():
    all_models = artifact_repository.list_models()
    id_models = [m for m in all_models if m.startswith("identity_")]
    meta_list = []
    for m in id_models:
        bundle = artifact_repository.load_model(m)
        meta_list.append(ModelMetadata(
            model_name=m,
            task="identity_resolution",
            algorithm=bundle.get("model_type", "unknown"),
            version=bundle.get("version", "1.0"),
            trained_at=bundle.get("trained_at", "N/A"),
            artifact_path=str(artifact_repository.models_dir / f"{m}.joblib"),
            is_active=True,
            evaluation_metrics=bundle.get("metrics")
        ))
    return ModelListResponse(
        models=meta_list,
        active_identity_model="identity_xgboost" if "identity_xgboost" in id_models else (id_models[0] if id_models else None)
    )

@router.post("/train", response_model=IdentityTrainResponse)
def train_identity_model(req: IdentityTrainRequest):
    return identity_resolution_service.train_model(
        model_type=req.model_type,
        test_size=req.test_size,
        random_seed=req.random_seed
    )

@router.post("/predict", response_model=IdentityPredictResponse)
def predict_identity(req: IdentityPredictRequest):
    return identity_resolution_service.predict_pair(
        features=req.features.model_dump(),
        model_type=req.model_type or "xgboost",
        pair_id=req.pair_id
    )

@router.post("/predict/batch", response_model=BatchIdentityPredictResponse)
def batch_predict_identity(req: BatchIdentityPredictRequest):
    if len(req.items) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000 items.")

    items_dict = [i.model_dump() for i in req.items]
    preds = identity_resolution_service.predict_batch(
        items=items_dict,
        model_type=req.model_type or "xgboost"
    )

    pos_count = sum(1 for p in preds if p.prediction_label == 1)
    neg_count = sum(1 for p in preds if p.prediction_label == 0)

    return BatchIdentityPredictResponse(
        total_items=len(preds),
        model_type=req.model_type or "xgboost",
        predictions=preds,
        positive_count=pos_count,
        negative_count=neg_count
    )

@router.get("/evaluation")
def get_identity_evaluation(model_type: str = Query("xgboost", description="Model type")):
    rep = artifact_repository.load_report(f"identity_eval_{model_type}")
    if not rep:
        # Check if model exists
        if artifact_repository.model_exists(f"identity_{model_type}"):
            bundle = artifact_repository.load_model(f"identity_{model_type}")
            return bundle.get("metrics", {})
        raise HTTPException(status_code=404, detail=f"No evaluation report found for {model_type}. Train the model first.")
    return rep

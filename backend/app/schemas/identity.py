from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class IdentityTrainRequest(BaseModel):
    model_type: str = Field("xgboost", description="Model algorithm: 'xgboost', 'random_forest', or 'logistic_regression'")
    test_size: float = Field(0.2, ge=0.1, le=0.5, description="Fraction of test data")
    random_seed: int = Field(42, description="Random seed for reproducibility")
    calibrate: bool = Field(True, description="Whether to evaluate probability calibration")

class ConfusionMatrixSchema(BaseModel):
    tn: int
    fp: int
    fn: int
    tp: int

class ModelEvaluationMetrics(BaseModel):
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    confusion_matrix: ConfusionMatrixSchema
    brier_score: Optional[float] = None
    test_size: int
    train_size: int
    positive_ratio_test: float
    feature_importances: Optional[Dict[str, float]] = None

class IdentityTrainResponse(BaseModel):
    model_id: str
    model_type: str
    version: str
    trained_at: str
    metrics: ModelEvaluationMetrics
    disclaimer: str = "Synthetic dataset for prototype demonstration only. Predictions do not establish identity."

class IdentityPairFeatures(BaseModel):
    same_device_observed: int = Field(0, ge=0, le=1)
    contact_overlap_jaccard: float = Field(..., ge=0.0, le=1.0)
    temporal_pattern_similarity: float = Field(..., ge=0.0, le=1.0)
    location_overlap_similarity: float = Field(..., ge=0.0, le=1.0)
    call_pattern_similarity: float = Field(..., ge=0.0, le=1.0)
    shared_case_count: int = Field(..., ge=0)
    days_between_observations: float = Field(..., ge=0.0)

class IdentityPredictRequest(BaseModel):
    model_type: Optional[str] = "xgboost"
    pair_id: Optional[str] = "PAIR-001"
    features: IdentityPairFeatures

class IdentityPredictResponse(BaseModel):
    pair_id: Optional[str]
    model_type: str
    model_version: str
    probability_same_identity: float
    prediction_label: int
    decision_threshold: float = 0.5
    feature_contributions: Optional[Dict[str, float]] = None
    interpretation: str
    disclaimer: str = "Model estimate based on synthetic training data. Not proof of identity."

class BatchIdentityPredictRequest(BaseModel):
    model_type: Optional[str] = "xgboost"
    items: List[IdentityPredictRequest]

class BatchIdentityPredictResponse(BaseModel):
    total_items: int
    model_type: str
    predictions: List[IdentityPredictResponse]
    positive_count: int
    negative_count: int
    disclaimer: str = "Model estimates based on synthetic data. Not proof of identity."

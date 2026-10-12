from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AnomalyTrainRequest(BaseModel):
    contamination: float = Field(0.09, gt=0.0, le=0.5, description="Expected proportion of outliers in the data")
    random_seed: int = Field(42, description="Random state for reproducibility")
    evaluate_against_synthetic_labels: bool = Field(True, description="Calculate metrics against synthetic ground truth")

class AnomalyTrainResponse(BaseModel):
    model_id: str
    contamination: float
    trained_at: str
    total_samples: int
    anomalies_detected: int
    anomaly_rate: float
    evaluation_metrics: Optional[Dict[str, float]] = None
    note: str = "Unsupervised Isolation Forest trained without labels. Labels used exclusively for post-hoc validation."

class AnomalyFeatureVector(BaseModel):
    entity_id: Optional[str] = "ENTITY-001"
    calls_per_day: float = Field(..., ge=0.0)
    unique_contacts_per_day: float = Field(..., ge=0.0)
    night_call_ratio: float = Field(..., ge=0.0, le=1.0)
    avg_call_duration_seconds: float = Field(..., ge=0.0)
    daily_contact_change_ratio: float = Field(..., ge=0.0, le=1.0)
    new_cell_count: int = Field(..., ge=0)

class AnomalyDetectRequest(BaseModel):
    items: List[AnomalyFeatureVector]

class AnomalyItemResult(BaseModel):
    entity_id: str
    anomaly_score: float # lower is more abnormal, or normalized 0 to 1
    is_anomaly: bool
    risk_level: str # LOW, MEDIUM, HIGH
    explanation: List[str]

class AnomalyDetectResponse(BaseModel):
    total_checked: int
    anomalies_found: int
    results: List[AnomalyItemResult]
    disclaimer: str = "Statistical anomaly flags highlight deviations from normal behavior, not criminal culpability."

class AnomalySummaryRecord(BaseModel):
    entity_id: str
    city: Optional[str] = None
    calls_per_day: float
    unique_contacts_per_day: float
    night_call_ratio: float
    avg_call_duration_seconds: float
    daily_contact_change_ratio: float
    new_cell_count: int
    anomaly_score: float
    is_anomaly: bool
    risk_level: str

class AnomalySummaryResponse(BaseModel):
    total_entities: int
    anomalies_count: int
    anomaly_percentage: float
    top_anomalies: List[AnomalySummaryRecord]
    feature_averages_normal: Dict[str, float]
    feature_averages_anomalous: Dict[str, float]

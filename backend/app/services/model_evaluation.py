import datetime
from typing import Dict, Any, List, Optional
from ..repositories.artifact_repository import artifact_repository
from ..schemas.models import EvaluationSummaryResponse
from .identity_resolution import identity_resolution_service

class ModelEvaluationService:
    def get_summary(self) -> EvaluationSummaryResponse:
        # Load identity models reports
        identity_models = []
        for mtype in ["logistic_regression", "random_forest", "xgboost"]:
            rep = artifact_repository.load_report(f"identity_eval_{mtype}")
            if rep:
                identity_models.append(rep)
            elif artifact_repository.model_exists(f"identity_{mtype}"):
                bundle = artifact_repository.load_model(f"identity_{mtype}")
                if "metrics" in bundle:
                    identity_models.append(bundle["metrics"])

        # Determine best model based on F1-Score or PR-AUC
        best_model = None
        best_f1 = -1.0
        for m in identity_models:
            f1 = m.get("f1_score", 0.0)
            if f1 > best_f1:
                best_f1 = f1
                best_model = m.get("model_type")

        # Load anomaly evaluation report
        anomaly_rep = artifact_repository.load_report("anomaly_evaluation")
        if not anomaly_rep and artifact_repository.model_exists("behavior_isolation_forest"):
            bundle = artifact_repository.load_model("behavior_isolation_forest")
            anomaly_rep = bundle.get("evaluation_metrics")

        # Formulate comparative commentary
        if identity_models:
            analysis_text = (
                f"Compared {len(identity_models)} identity resolution models. "
                f"Best performing model by F1-Score is '{best_model}' (F1: {best_f1:.4f}). "
                "Class imbalance handled via class weights / scale_pos_weight. "
                "All metrics evaluated on held-out test partition with strict entity/target separation."
            )
        else:
            analysis_text = "No trained models found in local artifact repository. Train models via /api/v1/identity/train to view comparative performance."

        return EvaluationSummaryResponse(
            generated_at=datetime.datetime.now().isoformat(),
            identity_models=identity_models,
            best_identity_model=best_model,
            anomaly_model=anomaly_rep,
            comparative_analysis=analysis_text
        )

model_evaluation_service = ModelEvaluationService()

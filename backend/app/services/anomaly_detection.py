import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

from ..core.config import settings
from ..core.logging_config import logger
from ..repositories.dataset_repository import dataset_repository
from ..repositories.artifact_repository import artifact_repository
from .preprocessing import preprocessing_service
from .feature_engineering import feature_engineering_service, ANOMALY_FEATURE_COLUMNS
from ..schemas.anomalies import (
    AnomalyTrainResponse, AnomalyDetectResponse,
    AnomalyItemResult, AnomalySummaryResponse, AnomalySummaryRecord
)

class AnomalyDetectionService:
    def __init__(self):
        self.model_name = "behavior_isolation_forest"

    def train_model(
        self,
        contamination: float = settings.DEFAULT_CONTAMINATION,
        random_seed: int = settings.RANDOM_SEED,
        evaluate: bool = True
    ) -> AnomalyTrainResponse:
        logger.info(f"Training unsupervised Isolation Forest with contamination={contamination}")
        df = dataset_repository.load_dataset("behavior_anomaly_features")
        feature_cols = feature_engineering_service.get_anomaly_feature_columns()

        X, y_synthetic = preprocessing_service.prepare_anomaly_data(df, feature_cols)

        # Build pipeline fitted on X (unsupervised, strictly no labels)
        preprocessor = preprocessing_service.create_numeric_pipeline(use_robust_scaler=True)
        X_proc = preprocessor.fit_transform(X)

        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=random_seed,
            n_estimators=150,
            n_jobs=-1
        )
        iso_forest.fit(X_proc)

        # In Isolation Forest: -1 is anomaly, 1 is inlier
        raw_preds = iso_forest.predict(X_proc)
        is_anomaly = (raw_preds == -1).astype(int)
        # raw decision function: lower means more anomalous
        scores = iso_forest.decision_function(X_proc)

        eval_metrics = None
        if evaluate and y_synthetic is not None:
            prec = float(precision_score(y_synthetic, is_anomaly, zero_division=0))
            rec = float(recall_score(y_synthetic, is_anomaly, zero_division=0))
            f1 = float(f1_score(y_synthetic, is_anomaly, zero_division=0))
            # Normalize inverted score for ROC-AUC
            roc = float(roc_auc_score(y_synthetic, -scores))
            eval_metrics = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(roc, 4),
                "true_anomaly_count": int((y_synthetic == 1).sum()),
                "predicted_anomaly_count": int(is_anomaly.sum())
            }

        version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle = {
            "model_id": f"anomaly_iso_{version}",
            "version": version,
            "clf": iso_forest,
            "preprocessor": preprocessor,
            "feature_cols": feature_cols,
            "contamination": contamination,
            "trained_at": datetime.datetime.now().isoformat(),
            "evaluation_metrics": eval_metrics
        }
        artifact_repository.save_model(self.model_name, bundle)
        if eval_metrics:
            artifact_repository.save_report("anomaly_evaluation", eval_metrics)

        return AnomalyTrainResponse(
            model_id=f"anomaly_iso_{version}",
            contamination=contamination,
            trained_at=datetime.datetime.now().isoformat(),
            total_samples=len(X),
            anomalies_detected=int(is_anomaly.sum()),
            anomaly_rate=round(float(is_anomaly.mean()), 4),
            evaluation_metrics=eval_metrics
        )

    def detect(self, items: List[Dict[str, Any]]) -> AnomalyDetectResponse:
        if not artifact_repository.model_exists(self.model_name):
            self.train_model()

        bundle = artifact_repository.load_model(self.model_name)
        clf = bundle["clf"]
        preprocessor = bundle["preprocessor"]
        feature_cols = bundle["feature_cols"]

        df_input = feature_engineering_service.construct_anomaly_features_df(items)
        X_proc = preprocessor.transform(df_input)

        raw_preds = clf.predict(X_proc)
        raw_scores = clf.decision_function(X_proc) # higher = normal, lower = abnormal

        results: List[AnomalyItemResult] = []
        anom_count = 0

        for i, (pred, score) in enumerate(zip(raw_preds, raw_scores)):
            is_anom = (pred == -1)
            if is_anom:
                anom_count += 1

            # Convert score to an anomaly risk index (0 to 1, where 1 is highest anomaly)
            risk_index = round(float(1.0 / (1.0 + np.exp(score * 4))), 4)
            if risk_index > 0.65:
                risk_lvl = "HIGH"
            elif risk_index > 0.45:
                risk_lvl = "MEDIUM"
            else:
                risk_lvl = "LOW"

            explanations = []
            row = df_input.iloc[i]
            if row.get("night_call_ratio", 0) > 0.6:
                explanations.append(f"Elevated night call ratio ({row['night_call_ratio']:.1%})")
            if row.get("calls_per_day", 0) > 60:
                explanations.append(f"Very high call volume ({row['calls_per_day']:.0f}/day)")
            if row.get("new_cell_count", 0) > 7:
                explanations.append(f"Frequent cell tower changes ({row['new_cell_count']} new cells)")
            if row.get("daily_contact_change_ratio", 0) > 0.8:
                explanations.append(f"Rapid contact churn rate ({row['daily_contact_change_ratio']:.1%})")
            if not explanations:
                explanations.append("Behavior consistent with standard subscriber baselines")

            ent_id = items[i].get("entity_id", f"ENT-{i+1}")
            results.append(AnomalyItemResult(
                entity_id=ent_id,
                anomaly_score=round(float(score), 4),
                is_anomaly=bool(is_anom),
                risk_level=risk_lvl,
                explanation=explanations
            ))

        return AnomalyDetectResponse(
            total_checked=len(items),
            anomalies_found=anom_count,
            results=results
        )

    def get_summary(self) -> AnomalySummaryResponse:
        df = dataset_repository.load_dataset("behavior_anomaly_features")
        feature_cols = feature_engineering_service.get_anomaly_feature_columns()

        if not artifact_repository.model_exists(self.model_name):
            self.train_model()

        bundle = artifact_repository.load_model(self.model_name)
        clf = bundle["clf"]
        preprocessor = bundle["preprocessor"]

        X, _ = preprocessing_service.prepare_anomaly_data(df, feature_cols)
        X_proc = preprocessor.transform(X)

        raw_preds = clf.predict(X_proc)
        raw_scores = clf.decision_function(X_proc)
        is_anom = (raw_preds == -1)

        summary_records = []
        for idx in range(len(df)):
            score = float(raw_scores[idx])
            anom = bool(is_anom[idx])
            risk_index = 1.0 / (1.0 + np.exp(score * 4))
            risk_lvl = "HIGH" if risk_index > 0.65 else "MEDIUM" if risk_index > 0.45 else "LOW"

            rec = AnomalySummaryRecord(
                entity_id=str(df.iloc[idx].get("entity_id", f"E{idx}")),
                city=str(df.iloc[idx].get("city", "Unknown")),
                calls_per_day=float(df.iloc[idx]["calls_per_day"]),
                unique_contacts_per_day=float(df.iloc[idx]["unique_contacts_per_day"]),
                night_call_ratio=float(df.iloc[idx]["night_call_ratio"]),
                avg_call_duration_seconds=float(df.iloc[idx]["avg_call_duration_seconds"]),
                daily_contact_change_ratio=float(df.iloc[idx]["daily_contact_change_ratio"]),
                new_cell_count=int(df.iloc[idx]["new_cell_count"]),
                anomaly_score=round(score, 4),
                is_anomaly=anom,
                risk_level=risk_lvl
            )
            summary_records.append(rec)

        # Sort by anomaly score ascending (most anomalous first)
        summary_records.sort(key=lambda x: x.anomaly_score)

        normal_df = df[~is_anom]
        anom_df = df[is_anom]

        avg_normal = {c: float(round(normal_df[c].mean(), 2)) for c in feature_cols}
        avg_anom = {c: float(round(anom_df[c].mean(), 2)) for c in feature_cols}

        return AnomalySummaryResponse(
            total_entities=len(df),
            anomalies_count=int(is_anom.sum()),
            anomaly_percentage=round(float(is_anom.mean() * 100), 2),
            top_anomalies=summary_records[:50],
            feature_averages_normal=avg_normal,
            feature_averages_anomalous=avg_anom
        )

anomaly_detection_service = AnomalyDetectionService()

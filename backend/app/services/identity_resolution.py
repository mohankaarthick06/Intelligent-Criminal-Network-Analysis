import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, precision_recall_curve, auc, confusion_matrix,
    brier_score_loss
)
from sklearn.pipeline import Pipeline

from ..core.config import settings
from ..core.exceptions import InsufficientDataError, ModelNotFoundError
from ..core.logging_config import logger
from ..repositories.dataset_repository import dataset_repository
from ..repositories.artifact_repository import artifact_repository
from .preprocessing import preprocessing_service
from .feature_engineering import feature_engineering_service, IDENTITY_FEATURE_COLUMNS
from ..schemas.identity import (
    ModelEvaluationMetrics, ConfusionMatrixSchema,
    IdentityTrainResponse, IdentityPredictResponse
)

class IdentityResolutionService:
    def __init__(self):
        self.default_model_type = "xgboost"

    def train_model(
        self,
        model_type: str = "xgboost",
        test_size: float = 0.2,
        random_seed: int = settings.RANDOM_SEED
    ) -> IdentityTrainResponse:
        logger.info(f"Training identity resolution model: {model_type} (test_size={test_size})")
        df = dataset_repository.load_dataset("identity_resolution_pairs")
        
        feature_cols = feature_engineering_service.get_identity_feature_columns()
        X, y = preprocessing_service.prepare_identity_data(df, feature_cols)

        if y is None or len(y.unique()) < 2:
            raise InsufficientDataError("Target variable 'same_identity_label' must contain at least 2 classes.")

        # Stratified train/test split to maintain class ratio
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_seed,
            stratify=y
        )

        # Build preprocessing pipeline fitted on X_train only
        preprocessor = preprocessing_service.create_numeric_pipeline()
        X_train_proc = preprocessor.fit_transform(X_train)
        X_test_proc = preprocessor.transform(X_test)

        # Calculate class weights for imbalance
        pos_count = int((y_train == 1).sum())
        neg_count = int((y_train == 0).sum())
        scale_pos = (neg_count / max(1, pos_count))

        # Instantiate algorithm
        mtype = model_type.lower()
        if mtype == "logistic_regression":
            clf = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_seed)
        elif mtype == "random_forest":
            clf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=random_seed, n_jobs=-1)
        elif mtype == "xgboost":
            clf = XGBClassifier(
                n_estimators=100,
                max_depth=4,
                scale_pos_weight=scale_pos,
                eval_metric="logloss",
                random_state=random_seed,
                tree_method="hist"
            )
        else:
            raise ValueError(f"Unsupported model type '{model_type}'. Choose 'xgboost', 'random_forest', or 'logistic_regression'.")

        clf.fit(X_train_proc, y_train)

        # Predictions & Probabilities
        y_pred = clf.predict(X_test_proc)
        y_prob = clf.predict_proba(X_test_proc)[:, 1] if hasattr(clf, "predict_proba") else y_pred.astype(float)

        # Evaluation metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc_val = float(roc_auc_score(y_test, y_prob)) if len(np.unique(y_test)) > 1 else 0.5
        
        # PR-AUC
        precisions, recalls, _ = precision_recall_curve(y_test, y_prob)
        pr_auc_val = float(auc(recalls, precisions))

        # Calibration (Brier Score)
        brier = float(brier_score_loss(y_test, y_prob))

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
        else:
            tn, fp, fn, tp = 0, 0, 0, 0

        # Feature importances
        feature_importances = {}
        if hasattr(clf, "feature_importances_"):
            for col, imp in zip(feature_cols, clf.feature_importances_):
                feature_importances[col] = float(round(imp, 4))
        elif hasattr(clf, "coef_"):
            for col, imp in zip(feature_cols, clf.coef_[0]):
                feature_importances[col] = float(round(abs(imp), 4))

        metrics = ModelEvaluationMetrics(
            model_type=mtype,
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            roc_auc=round(roc_auc_val, 4),
            pr_auc=round(pr_auc_val, 4),
            confusion_matrix=ConfusionMatrixSchema(tn=tn, fp=fp, fn=fn, tp=tp),
            brier_score=round(brier, 4),
            test_size=len(y_test),
            train_size=len(y_train),
            positive_ratio_test=round(float((y_test == 1).mean()), 4),
            feature_importances=feature_importances
        )

        version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        model_id = f"identity_{mtype}_{version}"

        # Save bundle
        artifact_bundle = {
            "model_id": model_id,
            "model_type": mtype,
            "version": version,
            "clf": clf,
            "preprocessor": preprocessor,
            "feature_cols": feature_cols,
            "metrics": metrics.model_dump(),
            "trained_at": datetime.datetime.now().isoformat()
        }
        artifact_repository.save_model(f"identity_{mtype}", artifact_bundle)
        artifact_repository.save_report(f"identity_eval_{mtype}", metrics.model_dump())

        return IdentityTrainResponse(
            model_id=model_id,
            model_type=mtype,
            version=version,
            trained_at=datetime.datetime.now().isoformat(),
            metrics=metrics
        )

    def predict_pair(
        self,
        features: Dict[str, Any],
        model_type: str = "xgboost",
        pair_id: Optional[str] = None
    ) -> IdentityPredictResponse:
        model_name = f"identity_{model_type.lower()}"
        if not artifact_repository.model_exists(model_name):
            # Auto-train default model if not existing
            self.train_model(model_type=model_type)

        bundle = artifact_repository.load_model(model_name)
        clf = bundle["clf"]
        preprocessor = bundle["preprocessor"]
        feature_cols = bundle["feature_cols"]

        df_input = feature_engineering_service.construct_identity_features_df([features])
        X_proc = preprocessor.transform(df_input)

        prob = float(clf.predict_proba(X_proc)[0, 1]) if hasattr(clf, "predict_proba") else 0.5
        pred_label = 1 if prob >= 0.5 else 0

        # Calculate simple feature contribution weights
        contributions = {}
        if hasattr(clf, "feature_importances_"):
            for col, val, imp in zip(feature_cols, df_input.iloc[0], clf.feature_importances_):
                contributions[col] = float(round(float(val) * float(imp), 4))
        elif hasattr(clf, "coef_"):
            for col, val, coef in zip(feature_cols, df_input.iloc[0], clf.coef_[0]):
                contributions[col] = float(round(float(val) * float(coef), 4))

        interpretation = (
            f"Strong candidate match (Estimated probability {prob:.1%})"
            if prob >= 0.7 else
            f"Moderate candidate match (Estimated probability {prob:.1%})"
            if prob >= 0.5 else
            f"Unlikely match (Estimated probability {prob:.1%})"
        )

        return IdentityPredictResponse(
            pair_id=pair_id,
            model_type=model_type,
            model_version=bundle.get("version", "v1.0"),
            probability_same_identity=round(prob, 4),
            prediction_label=pred_label,
            decision_threshold=0.5,
            feature_contributions=contributions,
            interpretation=interpretation
        )

    def predict_batch(
        self,
        items: List[Dict[str, Any]],
        model_type: str = "xgboost"
    ) -> List[IdentityPredictResponse]:
        results = []
        for item in items:
            features = item.get("features", item)
            pair_id = item.get("pair_id", None)
            res = self.predict_pair(features=features, model_type=model_type, pair_id=pair_id)
            results.append(res)
        return results

identity_resolution_service = IdentityResolutionService()

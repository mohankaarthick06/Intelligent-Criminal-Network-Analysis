import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from ..repositories.dataset_repository import dataset_repository
from ..schemas.datasets import DatasetValidationIssue, ValidationResultResponse, QualityReportResponse
from ..core.logging_config import logger

EXPECTED_SCHEMAS = {
    "cdr": [
        "cdr_id", "case_id", "caller_person_id", "caller_number", "receiver_person_id",
        "receiver_number", "call_timestamp", "call_duration_seconds", "call_type",
        "cell_id", "caller_imei", "cell_city", "cell_state", "cell_pincode",
        "cell_latitude", "cell_longitude"
    ],
    "phone_device_history": [
        "history_id", "person_id", "phone_number", "imei", "device_id",
        "start_date", "end_date", "change_reason", "primary_city", "primary_state",
        "primary_pincode", "primary_latitude", "primary_longitude"
    ],
    "imei_summary": [
        "imei", "tac", "device_id", "cdr_event_count", "unique_phone_numbers", "unique_cells"
    ],
    "identity_resolution_pairs": [
        "record_a", "record_b", "same_device_observed", "contact_overlap_jaccard",
        "temporal_pattern_similarity", "location_overlap_similarity", "call_pattern_similarity",
        "shared_case_count", "days_between_observations", "same_identity_label"
    ],
    "behavior_anomaly_features": [
        "entity_id", "calls_per_day", "unique_contacts_per_day", "night_call_ratio",
        "avg_call_duration_seconds", "daily_contact_change_ratio", "new_cell_count",
        "synthetic_anomaly_label"
    ],
    "synthetic_location_reference": [
        "city", "state", "pincode", "latitude", "longitude"
    ]
}

class DataValidationService:
    @staticmethod
    def validate_dataset(dataset_name: str, df: pd.DataFrame = None) -> ValidationResultResponse:
        if df is None:
            df = dataset_repository.load_dataset(dataset_name)

        issues: List[DatasetValidationIssue] = []
        clean_name = dataset_name.lower().replace(".csv", "")

        # 1. Non-empty check
        if len(df) == 0:
            issues.append(DatasetValidationIssue(
                check_name="empty_table_check",
                status="FAIL",
                message="Dataset has 0 rows."
            ))
            return ValidationResultResponse(
                dataset_name=dataset_name,
                is_valid=False,
                total_checks=1,
                passed_checks=0,
                failed_checks=1,
                issues=issues
            )
        else:
            issues.append(DatasetValidationIssue(
                check_name="empty_table_check",
                status="PASS",
                message=f"Dataset contains {len(df)} rows."
            ))

        # 2. Schema / Required columns check
        if clean_name in EXPECTED_SCHEMAS:
            expected_cols = EXPECTED_SCHEMAS[clean_name]
            missing_cols = [c for c in expected_cols if c not in df.columns]
            if missing_cols:
                issues.append(DatasetValidationIssue(
                    check_name="schema_expected_columns",
                    status="FAIL",
                    message=f"Missing expected columns: {missing_cols}",
                    details={"missing_columns": missing_cols}
                ))
            else:
                issues.append(DatasetValidationIssue(
                    check_name="schema_expected_columns",
                    status="PASS",
                    message="All expected schema columns are present."
                ))

        # 3. Duplicate row check
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            issues.append(DatasetValidationIssue(
                check_name="duplicate_rows_check",
                status="WARN",
                message=f"Found {dup_count} duplicate rows."
            ))
        else:
            issues.append(DatasetValidationIssue(
                check_name="duplicate_rows_check",
                status="PASS",
                message="No duplicate rows found."
            ))

        # 4. Latitude / Longitude validity checks
        lat_cols = [c for c in df.columns if "latitude" in c.lower() or c.lower() == "lat"]
        lon_cols = [c for c in df.columns if "longitude" in c.lower() or c.lower() == "lon" or c.lower() == "lng"]

        for col in lat_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = ((df[col] < -90) | (df[col] > 90)).sum()
                if invalid > 0:
                    issues.append(DatasetValidationIssue(
                        check_name=f"latitude_range_{col}",
                        status="FAIL",
                        message=f"Column {col} has {invalid} values outside [-90, 90]."
                    ))
                else:
                    issues.append(DatasetValidationIssue(
                        check_name=f"latitude_range_{col}",
                        status="PASS",
                        message=f"Latitude column {col} is within valid bounds [-90, 90]."
                    ))

        for col in lon_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = ((df[col] < -180) | (df[col] > 180)).sum()
                if invalid > 0:
                    issues.append(DatasetValidationIssue(
                        check_name=f"longitude_range_{col}",
                        status="FAIL",
                        message=f"Column {col} has {invalid} values outside [-180, 180]."
                    ))
                else:
                    issues.append(DatasetValidationIssue(
                        check_name=f"longitude_range_{col}",
                        status="PASS",
                        message=f"Longitude column {col} is within valid bounds [-180, 180]."
                    ))

        # 5. Timestamp validation
        time_cols = [c for c in df.columns if "timestamp" in c.lower() or "date" in c.lower()]
        for col in time_cols:
            try:
                # Test parse first 100 non-null values
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    pd.to_datetime(sample)
                    issues.append(DatasetValidationIssue(
                        check_name=f"timestamp_format_{col}",
                        status="PASS",
                        message=f"Timestamp column {col} matches valid date/time format."
                    ))
            except Exception as e:
                issues.append(DatasetValidationIssue(
                    check_name=f"timestamp_format_{col}",
                    status="WARN",
                    message=f"Timestamp column {col} contains invalid date formats: {str(e)}"
                ))

        # 6. Target distribution check if classification dataset
        if "same_identity_label" in df.columns:
            counts = df["same_identity_label"].value_counts().to_dict()
            if len(counts) < 2:
                issues.append(DatasetValidationIssue(
                    check_name="target_binary_classes",
                    status="FAIL",
                    message="Target column same_identity_label does not contain both classes (0 and 1)."
                ))
            else:
                issues.append(DatasetValidationIssue(
                    check_name="target_binary_classes",
                    status="PASS",
                    message=f"Target column classes present: {counts}"
                ))

        if "synthetic_anomaly_label" in df.columns:
            counts = df["synthetic_anomaly_label"].value_counts().to_dict()
            issues.append(DatasetValidationIssue(
                check_name="anomaly_label_distribution",
                status="PASS",
                message=f"Synthetic anomaly labels present: {counts}"
            ))

        failed_count = sum(1 for i in issues if i.status == "FAIL")
        passed_count = sum(1 for i in issues if i.status == "PASS")
        is_valid = failed_count == 0

        return ValidationResultResponse(
            dataset_name=dataset_name,
            is_valid=is_valid,
            total_checks=len(issues),
            passed_checks=passed_count,
            failed_checks=failed_count,
            issues=issues
        )

    @staticmethod
    def get_quality_report(dataset_name: str) -> QualityReportResponse:
        df = dataset_repository.load_dataset(dataset_name)
        val_result = DataValidationService.validate_dataset(dataset_name, df)

        total_cells = df.size
        missing_cells = int(df.isnull().sum().sum())
        missing_pct = float(round((missing_cells / total_cells) * 100, 2)) if total_cells > 0 else 0.0
        dup_rows = int(df.duplicated().sum())

        # Calculate a 0-100 score
        score = 100.0
        # Deduct for missing cells
        score -= min(30.0, missing_pct * 2.0)
        # Deduct for duplicate rows
        dup_pct = (dup_rows / len(df)) * 100 if len(df) > 0 else 0
        score -= min(30.0, dup_pct * 3.0)
        # Deduct for failed validation checks
        score -= (val_result.failed_checks * 15.0)
        score = float(max(0.0, round(score, 1)))

        recommendations = []
        if missing_cells > 0:
            recommendations.append(f"Handle {missing_cells} missing values using appropriate domain imputation.")
        if dup_rows > 0:
            recommendations.append(f"Remove {dup_rows} duplicate rows prior to downstream modeling.")
        if val_result.failed_checks > 0:
            recommendations.append("Resolve schema/range check failures before training production pipelines.")
        if not recommendations:
            recommendations.append("Dataset passed all standard quality and schema checks.")

        return QualityReportResponse(
            dataset_name=dataset_name,
            row_count=len(df),
            column_count=len(df.columns),
            duplicate_rows=dup_rows,
            missing_cells_total=missing_cells,
            missing_cells_percentage=missing_pct,
            integrity_score=score,
            checks=val_result.issues,
            recommendations=recommendations
        )

data_validation_service = DataValidationService()

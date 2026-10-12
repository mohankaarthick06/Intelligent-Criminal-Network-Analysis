from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ColumnDetail(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_percentage: float
    unique_count: int
    sample_values: List[Any]

class DatasetSummaryResponse(BaseModel):
    name: str
    row_count: int
    column_count: int
    columns: List[str]
    column_details: List[ColumnDetail]
    file_size_bytes: int
    preview: List[Dict[str, Any]]

class DatasetValidationIssue(BaseModel):
    check_name: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str
    details: Optional[Dict[str, Any]] = None

class ValidationResultResponse(BaseModel):
    dataset_name: str
    is_valid: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    issues: List[DatasetValidationIssue]

class QualityReportResponse(BaseModel):
    dataset_name: str
    row_count: int
    column_count: int
    duplicate_rows: int
    missing_cells_total: int
    missing_cells_percentage: float
    integrity_score: float # 0 to 100
    checks: List[DatasetValidationIssue]
    recommendations: List[str]

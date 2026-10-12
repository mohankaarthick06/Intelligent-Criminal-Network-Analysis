import pytest
import pandas as pd
from backend.app.services.data_validation import data_validation_service
from backend.app.core.exceptions import DatasetNotFoundError

def test_validate_valid_dataset():
    res = data_validation_service.validate_dataset("identity_resolution_pairs")
    assert res.is_valid is True
    assert res.total_checks > 0
    assert res.failed_checks == 0

def test_validate_empty_dataframe():
    empty_df = pd.DataFrame()
    res = data_validation_service.validate_dataset("empty_dummy", empty_df)
    assert res.is_valid is False
    assert any("empty_table_check" in issue.check_name for issue in res.issues)

def test_validate_missing_columns():
    bad_df = pd.DataFrame({"col_a": [1, 2], "col_b": [3, 4]})
    res = data_validation_service.validate_dataset("cdr", bad_df)
    assert res.is_valid is False
    assert any("schema_expected_columns" in issue.check_name and issue.status == "FAIL" for issue in res.issues)

def test_validate_out_of_bounds_coordinates():
    bad_coords_df = pd.DataFrame({
        "city": ["TestCity"],
        "state": ["TestState"],
        "pincode": [123456],
        "latitude": [195.0], # invalid > 90
        "longitude": [78.0]
    })
    res = data_validation_service.validate_dataset("synthetic_location_reference", bad_coords_df)
    assert res.is_valid is False
    assert any("latitude_range" in issue.check_name and issue.status == "FAIL" for issue in res.issues)

def test_get_quality_report():
    report = data_validation_service.get_quality_report("behavior_anomaly_features")
    assert report.dataset_name == "behavior_anomaly_features"
    assert report.row_count > 0
    assert report.integrity_score >= 0.0
    assert len(report.checks) > 0

def test_validate_nonexistent_dataset():
    with pytest.raises(DatasetNotFoundError):
        data_validation_service.validate_dataset("completely_nonexistent_dataset_name")

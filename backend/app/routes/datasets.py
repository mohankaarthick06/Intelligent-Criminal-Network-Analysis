from fastapi import APIRouter, Path, HTTPException
from typing import List, Dict, Any
from ..schemas.datasets import DatasetSummaryResponse, ValidationResultResponse, QualityReportResponse
from ..repositories.dataset_repository import dataset_repository
from ..services.data_loader import data_loader_service
from ..services.data_validation import data_validation_service

router = APIRouter(prefix="/api/v1/datasets", tags=["Datasets"])

@router.get("", response_model=List[str])
def list_datasets():
    return dataset_repository.list_datasets()

@router.get("/{dataset_name}/summary", response_model=DatasetSummaryResponse)
def get_dataset_summary(dataset_name: str = Path(..., description="Dataset name, e.g. cdr or cdr.csv")):
    return data_loader_service.get_summary(dataset_name)

@router.post("/{dataset_name}/validate", response_model=ValidationResultResponse)
def validate_dataset(dataset_name: str = Path(..., description="Dataset name, e.g. cdr")):
    return data_validation_service.validate_dataset(dataset_name)

@router.get("/{dataset_name}/quality", response_model=QualityReportResponse)
def get_dataset_quality(dataset_name: str = Path(..., description="Dataset name, e.g. cdr")):
    return data_validation_service.get_quality_report(dataset_name)

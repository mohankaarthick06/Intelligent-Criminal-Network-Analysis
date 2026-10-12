import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..repositories.dataset_repository import dataset_repository
from ..schemas.datasets import DatasetSummaryResponse, ColumnDetail

class DataLoaderService:
    @staticmethod
    def get_summary(dataset_name: str) -> DatasetSummaryResponse:
        df = dataset_repository.load_dataset(dataset_name)
        file_path = dataset_repository.get_dataset_path(dataset_name)
        file_size = file_path.stat().st_size if file_path.exists() else 0

        column_details: List[ColumnDetail] = []
        for col in df.columns:
            missing_count = int(df[col].isnull().sum())
            missing_pct = float(round((missing_count / len(df)) * 100, 2)) if len(df) > 0 else 0.0
            unique_count = int(df[col].nunique(dropna=True))
            sample_vals = df[col].dropna().head(3).tolist()
            # Convert numpy types to native python for JSON serialization
            sample_vals = [int(v) if isinstance(v, (np.integer, int)) else float(v) if isinstance(v, (np.floating, float)) else str(v) for v in sample_vals]

            column_details.append(
                ColumnDetail(
                    name=col,
                    dtype=str(df[col].dtype),
                    missing_count=missing_count,
                    missing_percentage=missing_pct,
                    unique_count=unique_count,
                    sample_values=sample_vals
                )
            )

        # Get preview top 10 rows
        preview_df = df.head(10).replace({np.nan: None})
        preview = preview_df.to_dict(orient="records")

        return DatasetSummaryResponse(
            name=dataset_name,
            row_count=len(df),
            column_count=len(df.columns),
            columns=list(df.columns),
            column_details=column_details,
            file_size_bytes=file_size,
            preview=preview
        )

data_loader_service = DataLoaderService()

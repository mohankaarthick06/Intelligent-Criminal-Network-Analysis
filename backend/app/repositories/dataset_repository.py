import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from ..core.config import settings
from ..core.exceptions import DatasetNotFoundError
from ..core.logging_config import logger

class DatasetRepository:
    def __init__(self, raw_dir: Path = settings.RAW_DATA_DIR, processed_dir: Path = settings.PROCESSED_DATA_DIR):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self._cache: Dict[str, pd.DataFrame] = {}

    def list_datasets(self) -> List[str]:
        """List all available CSV datasets in raw and processed dirs."""
        datasets = set()
        if self.raw_dir.exists():
            for f in self.raw_dir.glob("*.csv"):
                datasets.add(f.stem)
        if self.processed_dir.exists():
            for f in self.processed_dir.glob("*.csv"):
                datasets.add(f.stem)
        return sorted(list(datasets))

    def get_dataset_path(self, dataset_name: str, prefer_processed: bool = False) -> Path:
        """Find the path to the CSV file."""
        # Sanitize dataset_name to prevent directory traversal
        sanitized_name = Path(dataset_name).name
        if not sanitized_name.endswith(".csv"):
            csv_name = f"{sanitized_name}.csv"
        else:
            csv_name = sanitized_name

        if prefer_processed:
            proc_path = self.processed_dir / csv_name
            if proc_path.exists():
                return proc_path

        raw_path = self.raw_dir / csv_name
        if raw_path.exists():
            return raw_path

        proc_path = self.processed_dir / csv_name
        if proc_path.exists():
            return proc_path

        raise DatasetNotFoundError(dataset_name)

    def load_dataset(self, dataset_name: str, use_cache: bool = True) -> pd.DataFrame:
        """Load a dataset safely as a DataFrame."""
        if use_cache and dataset_name in self._cache:
            return self._cache[dataset_name].copy()

        path = self.get_dataset_path(dataset_name)
        try:
            df = pd.read_csv(path)
            if use_cache:
                self._cache[dataset_name] = df.copy()
            return df
        except Exception as e:
            logger.error(f"Failed to read dataset {dataset_name} at {path}: {e}")
            raise DatasetNotFoundError(f"{dataset_name} (Error: {str(e)})")

    def save_processed(self, dataset_name: str, df: pd.DataFrame) -> Path:
        """Save a processed dataset."""
        sanitized_name = Path(dataset_name).name
        if not sanitized_name.endswith(".csv"):
            sanitized_name = f"{sanitized_name}.csv"
        dest_path = self.processed_dir / sanitized_name
        df.to_csv(dest_path, index=False)
        self._cache[dest_path.stem] = df.copy()
        logger.info(f"Saved processed dataset {dest_path.stem} to {dest_path}")
        return dest_path

    def clear_cache(self):
        self._cache.clear()

dataset_repository = DatasetRepository()

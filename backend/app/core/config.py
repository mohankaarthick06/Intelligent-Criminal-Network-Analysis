import os
from pathlib import Path
from pydantic import BaseModel, ConfigDict

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    APP_NAME: str = "Intelligent Criminal Network Analysis"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Storage Paths
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    MODELS_DIR: Path = BASE_DIR / "models"
    REPORTS_DIR: Path = BASE_DIR / "reports"

    # Reproducibility & Limits
    RANDOM_SEED: int = 42
    DEFAULT_CONTAMINATION: float = 0.09
    MAX_BATCH_PREDICT_SIZE: int = 1000
    MAX_GRAPH_NODES_VISUALIZATION: int = 500

settings = Settings()

# Ensure directories exist
settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

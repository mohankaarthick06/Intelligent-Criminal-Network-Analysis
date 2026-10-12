import json
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..core.config import settings
from ..core.exceptions import ModelNotFoundError
from ..core.logging_config import logger

class ArtifactRepository:
    def __init__(self, models_dir: Path = settings.MODELS_DIR, reports_dir: Path = settings.REPORTS_DIR):
        self.models_dir = Path(models_dir)
        self.reports_dir = Path(reports_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_model(self, model_name: str, model_artifact: Any) -> Path:
        """Save a model object (e.g., pipeline or dict containing model and preprocessor) to disk."""
        sanitized = Path(model_name).name
        if not sanitized.endswith(".joblib"):
            sanitized = f"{sanitized}.joblib"
        path = self.models_dir / sanitized
        joblib.dump(model_artifact, path)
        logger.info(f"Model saved to {path}")
        return path

    def load_model(self, model_name: str) -> Any:
        """Load a saved model artifact from disk."""
        sanitized = Path(model_name).name
        if not sanitized.endswith(".joblib"):
            sanitized = f"{sanitized}.joblib"
        path = self.models_dir / sanitized
        if not path.exists():
            raise ModelNotFoundError(model_name)
        try:
            return joblib.load(path)
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise ModelNotFoundError(f"{model_name} (Corrupted or invalid: {str(e)})")

    def model_exists(self, model_name: str) -> bool:
        sanitized = Path(model_name).name
        if not sanitized.endswith(".joblib"):
            sanitized = f"{sanitized}.joblib"
        return (self.models_dir / sanitized).exists()

    def list_models(self) -> List[str]:
        return [f.stem for f in self.models_dir.glob("*.joblib")]

    def save_report(self, report_name: str, data: Dict[str, Any]) -> Path:
        sanitized = Path(report_name).name
        if not sanitized.endswith(".json"):
            sanitized = f"{sanitized}.json"
        path = self.reports_dir / sanitized
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Report saved to {path}")
        return path

    def load_report(self, report_name: str) -> Dict[str, Any]:
        sanitized = Path(report_name).name
        if not sanitized.endswith(".json"):
            sanitized = f"{sanitized}.json"
        path = self.reports_dir / sanitized
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_reports(self) -> List[str]:
        return [f.stem for f in self.reports_dir.glob("*.json")]

artifact_repository = ArtifactRepository()

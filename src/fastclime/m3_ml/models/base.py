from pathlib import Path
import joblib
import json


class BaseModel:
    """Mixin con helpers de save / load / metrics."""

    @classmethod
    def load(cls, folder: Path):
        return joblib.load(folder / "model.pkl")

    def save(self, folder: Path, metrics: dict):
        folder.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, folder / "model.pkl")
        Path(folder / "metrics.json").write_text(json.dumps(metrics, indent=2))

import pandas as pd
from pathlib import Path
from typing import Optional
from .features import make_features
from .models.base import BaseModel
from .const import MODELS_DIR
from fastclime.m0_storage.catalog import DataCatalog

def load_latest(model_name: str) -> BaseModel:
    """Loads the latest model from the given model_name directory."""
    model_dir = max((MODELS_DIR / model_name).iterdir())
    return BaseModel.load(model_dir)


def predict_batch(model_name: str, csv_in: Path, csv_out: Path, catalog: Optional[DataCatalog] = None) -> None:
    """Generates predictions for a CSV file and saves them to another CSV file."""
    df_raw = pd.read_csv(csv_in, parse_dates=["date"])
    X = make_features(df_raw)

    features_to_drop = ["parcel_id", "zone_id"]
    features_to_drop_existing = [f for f in features_to_drop if f in X.columns]
    X_pred = X.drop(columns=features_to_drop_existing)

    mdl = load_latest(model_name)
    preds = (
        mdl.predict_proba(X_pred)[:, 1]
        if hasattr(mdl, "predict_proba")
        else mdl.predict(X_pred)
    )
    df_raw["prediction"] = preds
    df_raw.to_csv(csv_out, index=False)

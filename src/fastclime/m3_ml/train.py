from datetime import date
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from .datasets import load_hourly_metrics, split_xy
from .features import make_features
from .models.stress_clf import StressClf
from .models.lamina_reg import LaminaReg
from .const import MODELS_DIR
from fastclime.m0_storage.catalog import DataCatalog, get_catalog

REGISTRY = {
    "stress_clf": StressClf,
    "lamina_reg": LaminaReg,
}

def _ensure_tables(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS metrics_hourly (
            ts TIMESTAMP,
            parcel_id TEXT,
            zone_id TEXT,
            deficit_mm_h DOUBLE,
            eto_mm_h DOUBLE,
            temp_c DOUBLE,
            rain_mm_h DOUBLE
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS plant_ndvi_daily (
            date DATE,
            parcel_id TEXT,
            zone_id TEXT,
            ndvi DOUBLE
        );
    """)


def train_one(
    model_name: str,
    overwrite: bool = False,
    catalog: Optional[DataCatalog] = None,
    output_dir: Optional[Path] = None,
    **kwargs: Any,
) -> Dict[str, float]:
    """Trains a single model and saves it to disk."""

    if catalog is None:
        catalog = get_catalog()

    with catalog.get_connection() as con:
        _ensure_tables(con)

    df = load_hourly_metrics(limit_years=3, db_path=catalog.db_path)

    if "stress_flag" not in df.columns:
        df["stress_flag"] = (df["deficit_now_mm"] > 5).astype(int)
    if "lamina_opt_mm" not in df.columns:
        df["lamina_opt_mm"] = df["deficit_now_mm"] * 0.8

    X_raw, y = split_xy(df, model_name)
    X = make_features(X_raw)

    features_to_drop = ["parcel_id", "zone_id"]
    features_to_drop_existing = [f for f in features_to_drop if f in X.columns]
    X_train = X.drop(columns=features_to_drop_existing)

    ModelCls = REGISTRY[model_name]
    # Filter kwargs for the model training
    model_kwargs = {
        k: v for k, v in kwargs.items() if k in ["n_estimators", "learning_rate"]
    }
    mdl, metrics = ModelCls.train(X_train, y, **model_kwargs)

    stamp = date.today().strftime("%Y%m%d")

    models_dir = output_dir if output_dir else MODELS_DIR
    folder = models_dir / model_name / stamp

    if folder.exists() and not overwrite:
        print(f"Model already exists in {folder}, skipping. Use --overwrite.")
        return metrics

    mdl.save(folder, metrics)

    # Save feature importance
    if hasattr(mdl, "feature_importances_"):
        imp_df = pd.DataFrame(
            {"feature": X_train.columns, "importance": mdl.feature_importances_}
        ).sort_values("importance", ascending=False)
        imp_df.to_csv(folder / "feature_importance.csv", index=False)

    print("Training finished.")
    return metrics


def train_all(overwrite: bool = False, **kwargs: Any) -> Dict[str, Dict[str, float]]:
    """Trains all models in the registry."""
    out = {}
    for name in REGISTRY:
        out[name] = train_one(name, overwrite=overwrite, **kwargs)
    return out

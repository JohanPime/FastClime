import pandas as pd
import numpy as np


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["doy"] = out.date.dt.dayofyear
    out["month"] = out.date.dt.month
    out["eto_et_c_ratio"] = np.clip(out.eto / (out.eto + 1e-6), 0, 10)
    # lag features (last 3 days deficit/ndvi)
    for lag in (1, 2, 3):
        out[f"deficit_lag{lag}"] = out.groupby("zone_id").deficit_now_mm.shift(lag)
        out[f"ndvi_lag{lag}"] = out.groupby("zone_id").ndvi.shift(lag)
    out = out.fillna(method="ffill").fillna(0)
    numeric = out.select_dtypes(include="number")
    return numeric

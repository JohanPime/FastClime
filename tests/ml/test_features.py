import pandas as pd
from fastclime.m3_ml.features import make_features


def test_make_features_no_nan():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                pd.Series(["2025-01-01", "2025-01-02", "2025-01-03"])
            ),
            "deficit_now_mm": [1, 2, 3],
            "eto": [4, 4, 4],
            "ndvi": [0.3, 0.35, 0.33],
            "temp_mean": [25, 26, 24],
            "rain_24h": [0, 5, 0],
            "zone_id": [1, 1, 1],
        }
    )
    out = make_features(df)
    assert out.isna().sum().sum() == 0


def test_make_features_correctness():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                pd.Series(["2025-01-01", "2025-01-02", "2025-01-03"])
            ),
            "deficit_now_mm": [1, 2, 3],
            "eto": [4, 4, 4],
            "ndvi": [0.3, 0.35, 0.33],
            "temp_mean": [25, 26, 24],
            "rain_24h": [0, 5, 0],
            "zone_id": [1, 1, 1],
        }
    )
    out = make_features(df)
    assert "doy" in out.columns
    assert "month" in out.columns
    assert "eto_et_c_ratio" in out.columns
    assert "deficit_lag1" in out.columns
    assert out["doy"].iloc[0] == 1
    assert out["month"].iloc[0] == 1
    assert out["deficit_lag1"].iloc[1] == 1
    assert out.select_dtypes(include="number").shape[1] == out.shape[1]

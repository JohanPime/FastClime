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

import pandas as pd
import numpy as np
from fastclime.m3_ml.serve import predict_batch
from fastclime.m3_ml.models.stress_clf import StressClf


def test_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    pd.DataFrame(
        {
            "date": ["2025-01-01"],
            "deficit_now_mm": [1],
            "eto": [4],
            "ndvi": [0.3],
            "temp_mean": [25],
            "rain_24h": [0],
            "zone_id": [1],
        }
    ).to_csv(csv_in, index=False)

    # Create a dummy model directory
    model_dir = tmp_path / "models" / "stress_clf" / "20250101"
    model_dir.mkdir(parents=True)

    # Create and fit a dummy model that can be loaded
    dummy_model = StressClf()
    # The number of features needs to match what make_features produces
    # make_features produces 14 features
    dummy_X = pd.DataFrame(np.random.rand(10, 14))
    dummy_y = pd.Series(np.random.randint(0, 2, 10))
    dummy_model.fit(dummy_X, dummy_y)
    dummy_model.save(model_dir, {})

    # Mock the load_latest function to return our dummy model from the temp path
    original_models_dir = predict_batch.__globals__["MODELS_DIR"]
    predict_batch.__globals__["MODELS_DIR"] = tmp_path / "models"

    try:
        predict_batch("stress_clf", csv_in, csv_out)
        assert "prediction" in pd.read_csv(csv_out).columns
    finally:
        # Restore the original MODELS_DIR
        predict_batch.__globals__["MODELS_DIR"] = original_models_dir

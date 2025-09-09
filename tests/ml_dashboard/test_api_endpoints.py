from fastapi.testclient import TestClient
from fastclime.m4_dashboard.app import app
import pandas as pd

# This is the key: we need to import the app once and reuse it
client = TestClient(app)

def test_get_predictions_ok(monkeypatch):
    """
    Test the /api/predictions/{zone_id} endpoint for a successful response.
    We patch the function in the module where it's used (the router).
    """
    from fastclime.m4_dashboard.api import router as api_router

    mock_data = {
        "ts": [pd.to_datetime("2025-01-01T12:00:00")],
        "zone_id": ["z"],
        "lamina_mm": [5.0]
    }
    mock_df = pd.DataFrame(mock_data)

    # Patch the read_duckdb function within the router's scope
    monkeypatch.setattr(api_router, "read_duckdb", lambda q, p: mock_df)

    r = client.get("/api/predictions/z")

    assert r.status_code == 200
    response_json = r.json()
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["lamina_mm"] == 5.0
    assert response_json["items"][0]["zone_id"] == "z"
    assert "2025-01-01T12:00:00" in response_json["items"][0]["ts"]

def test_get_predictions_not_found(monkeypatch):
    """
    Test the /api/predictions/{zone_id} endpoint for a 404 response.
    """
    from fastclime.m4_dashboard.api import router as api_router

    # Patch read_duckdb to return an empty DataFrame
    monkeypatch.setattr(api_router, "read_duckdb", lambda q, p: pd.DataFrame())

    r = client.get("/api/predictions/nonexistent_zone")

    assert r.status_code == 404
    assert r.json()["detail"] == "Zone not found"

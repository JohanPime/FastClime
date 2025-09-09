from fastapi import APIRouter, HTTPException
from fastclime.m4_dashboard.utils import read_duckdb
from fastclime.m4_dashboard.api.models import PredictionResponse

router = APIRouter(tags=["Predictions"])

@router.get("/predictions/{zone_id}", response_model=PredictionResponse)
def get_predictions(zone_id: str):
    query = "SELECT * FROM predictions WHERE zone_id = ? ORDER BY ts DESC LIMIT 168"
    df = read_duckdb(query, (zone_id,))
    if df.empty:
        raise HTTPException(404, "Zone not found")
    return PredictionResponse.from_df(df)

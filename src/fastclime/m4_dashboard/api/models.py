from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from typing import List

class PredictionItem(BaseModel):
    """A single prediction item for a given timestamp and zone."""
    ts: datetime = Field(..., description="The timestamp of the prediction.")
    zone_id: str = Field(..., description="The identifier for the zone.")
    lamina_mm: float = Field(..., description="The predicted irrigation lamina in millimeters.")

class PredictionResponse(BaseModel):
    """The response model containing a list of prediction items."""
    items: List[PredictionItem]

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> "PredictionResponse":
        """Creates a PredictionResponse instance from a pandas DataFrame."""
        # Ensure 'ts' column is of datetime type for correct serialization
        if not pd.api.types.is_datetime64_any_dtype(df.get("ts")):
            df["ts"] = pd.to_datetime(df["ts"])

        # Convert dataframe records to a list of PredictionItem models
        prediction_items = [PredictionItem(**row) for row in df.to_dict(orient="records")]
        return cls(items=prediction_items)

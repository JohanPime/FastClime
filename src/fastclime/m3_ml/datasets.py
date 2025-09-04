import duckdb
import pandas as pd
from .const import TARGETS
from fastclime.m0_storage import DATA_DIR


from pathlib import Path
from typing import Optional


def load_hourly_metrics(
    limit_years: int | None = None, db_path: Optional[Path] = None
) -> pd.DataFrame:
    """JOIN metrics_hourly + plant_ndvi_daily en una tabla diaria."""
    con = duckdb.connect(":memory:")
    con.execute("INSTALL spatial; LOAD spatial;")  # si usas extensiones

    if db_path is None:
        db_path = DATA_DIR / "catalog.db"

    print(f"Loading data from {db_path}")
    con.execute(f"ATTACH '{db_path}';")
    base = """
        SELECT date_trunc('day', ts) AS date,
               parcel_id, zone_id,
               SUM(deficit_mm_h) AS deficit_now_mm,
               AVG(eto_mm_h)     AS eto,
               AVG(temp_c)       AS temp_mean,
               SUM(rain_mm_h)    AS rain_24h
        FROM metrics_hourly
        GROUP BY 1,2,3
    """
    ndvi = """
        SELECT date, parcel_id, zone_id, ndvi
        FROM plant_ndvi_daily
    """
    df = con.execute(
        f"""
        SELECT * FROM ({base}) m
        LEFT JOIN ({ndvi}) n
        USING(date, parcel_id, zone_id)
    """
    ).df()
    if limit_years:
        df = df[df.date.dt.year >= (df.date.dt.year.max() - limit_years)]
    return df


def split_xy(df: pd.DataFrame, model_name: str):
    target = TARGETS[model_name]
    y = df[target]
    X = df.drop(columns=list(TARGETS.values()))
    return X, y

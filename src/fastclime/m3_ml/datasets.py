import duckdb
import pandas as pd
from .const import TARGETS


def load_hourly_metrics(limit_years: int | None = None) -> pd.DataFrame:
    """JOIN metrics_hourly + plant_ndvi_daily en una tabla diaria."""
    con = duckdb.connect(":memory:")
    con.execute("INSTALL spatial; LOAD spatial;")  # si usas extensiones
    path = "fastclime_data/catalog.db"  # picked from settings
    con.execute(f"ATTACH '{path}' AS cat;")
    base = """
        SELECT date_trunc('day', ts) AS date,
               parcel_id, zone_id,
               SUM(deficit_mm_h) AS deficit_now_mm,
               AVG(eto_mm_h)     AS eto,
               AVG(temp_c)       AS temp_mean,
               SUM(rain_mm_h)    AS rain_24h
        FROM cat.metrics_hourly
        GROUP BY 1,2,3
    """
    ndvi = """
        SELECT date, parcel_id, zone_id, ndvi
        FROM cat.plant_ndvi_daily
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

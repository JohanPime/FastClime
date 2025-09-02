"""Orchestration logic for the dynamic model."""

import pandas as pd
from fastclime.core.logging import get_logger
from ..m0_storage.catalog import DataCatalog
from . import equations

log = get_logger(__name__)


def _init_tables(con):
    """Creates the output tables if they don't exist."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics_hourly (
            ts TIMESTAMP,
            parcel_id VARCHAR,
            eto_mm_h DOUBLE,
            etc_mm_h DOUBLE,
            pe_mm_h DOUBLE,
            depletion_mm DOUBLE,
            ks DOUBLE,
            ish DOUBLE,
            PRIMARY KEY (ts, parcel_id)
        );
    """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS deficit_proj (
            date DATE,
            parcel_id VARCHAR,
            scenario VARCHAR,
            deficit_mm DOUBLE,
            PRIMARY KEY (date, parcel_id, scenario)
        );
    """
    )


def run_hourly(start_ts: str, end_ts: str, parcel_id: str):
    """
    Runs the hourly water balance simulation.
    """
    log.info(
        f"Running hourly simulation from {start_ts} to {end_ts} for parcel {parcel_id}..."
    )
    catalog = DataCatalog()
    con = catalog.get_connection()
    _init_tables(con)

    # --- 1. Fetch input data (placeholders for now) ---
    log.warning("Using placeholder climate and parcel data.")
    # In a real scenario, this would query DuckDB:
    # "SELECT * FROM climate_hourly WHERE ts BETWEEN ? AND ? AND parcel_id = ?"
    # "SELECT lat FROM parcels WHERE id = ?"
    # "SELECT kc FROM crops_kc WHERE ..."
    climate_df = pd.DataFrame(
        {
            "ts": pd.to_datetime(pd.date_range(start=start_ts, end=end_ts, freq="h")),
            "T2M": 25.0,
            "RH2M": 60.0,
            "WS2M": 2.0,
            "ALLSKY_SFC_SW_DWN": 500.0,
            "PRECTOTCORR": 0.1,
            "PS": 101.3,
        }
    )
    parcel_lat = 34.0  # Placeholder latitude for LA
    crop_kc = 0.8  # Placeholder Kc

    # --- 2. Run simulation ---
    results = []
    # Get last known depletion or start from 0
    # prev_depletion = con.execute("...").fetchone() or (0,)
    prev_depletion = 0.0

    for _, row in climate_df.iterrows():
        eto = equations.eto_penman_monteith(
            ts=row["ts"],
            lat=parcel_lat,
            temp_c=row["T2M"],
            rh_percent=row["RH2M"],
            wind_ms=row["WS2M"],
            solar_rad_w_m2=row["ALLSKY_SFC_SW_DWN"],
            atmos_press_kpa=row["PS"],
        )
        etc = equations.etc(kc=crop_kc, eto=eto)
        pe = row["PRECTOTCORR"]  # Assume all precipitation is effective for now

        depletion, ks, ish = equations.soil_water_balance(
            prev_D=prev_depletion, etc=etc, Pe=pe, irrigation_mm=0
        )

        results.append(
            {
                "ts": row["ts"],
                "parcel_id": parcel_id,
                "eto_mm_h": eto,
                "etc_mm_h": etc,
                "pe_mm_h": pe,
                "depletion_mm": depletion,
                "ks": ks,
                "ish": ish,
            }
        )
        prev_depletion = depletion

    # --- 3. Write results to DuckDB ---
    if results:
        df_results = pd.DataFrame(results)
        # Use INSERT OR REPLACE to be idempotent
        con.execute("INSERT OR REPLACE INTO metrics_hourly SELECT * FROM df_results")
        log.info(f"Successfully wrote {len(df_results)} rows to 'metrics_hourly'.")

    con.close()
    return {"status": "complete", "rows_written": len(results)}


def project_deficit(days: int = 7):
    """
    Projects the water deficit for a number of days into the future. (Placeholder)
    """
    log.info(f"Projecting deficit for {days} days... (placeholder)")
    # This would be similar to run_hourly but use forecast data and assume no irrigation.
    return {"status": "complete", "scenarios_run": 1}

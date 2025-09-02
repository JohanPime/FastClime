"""Tests for the M2 Dynamic Model."""

import pytest
import pandas as pd
from fastclime.m2_dynamic import equations


def test_eto_penman_monteith_fao56_example19():
    """
    Tests the eto_penman_monteith function against the values from
    Example 19 of the FAO-56 paper (14:00-15:00h).
    """
    # --- Inputs from FAO-56 Example 19 ---
    # Location: N'Diaye, Senegal
    lat_deg = 16.21  # 16°13'N
    elevation_m = 8

    # Timestamp: 1 October, 14:30 (midpoint of 14:00-15:00)
    # The year doesn't matter for the calculation itself, just the day.
    ts = pd.Timestamp("2024-10-01 14:30:00")

    # Climate data
    temp_c = 38.0
    rh_percent = 52.0
    wind_ms = 3.3
    solar_rad_mj_m2_h = 2.450

    # Convert radiation to W/m2 for the function input
    solar_rad_w_m2 = solar_rad_mj_m2_h / 0.0036

    # Atmospheric pressure from elevation (Eq. 7)
    atmos_press_kpa = 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26

    # --- Calculation ---
    eto_mm_h = equations.eto_penman_monteith(
        ts=ts,
        lat=lat_deg,
        temp_c=temp_c,
        rh_percent=rh_percent,
        wind_ms=wind_ms,
        solar_rad_w_m2=solar_rad_w_m2,
        atmos_press_kpa=atmos_press_kpa,
    )

    # --- Assertion ---
    # The FAO paper calculates ETo = 0.63 mm/hour
    expected_eto = 0.63
    # Allow a small tolerance due to potential differences in constants or float precision
    assert eto_mm_h == pytest.approx(expected_eto, abs=0.05)


def test_soil_water_balance():
    """
    Tests the soil_water_balance function with a simple scenario.
    """
    prev_D = 10.0  # 10mm depletion
    etc = 5.0  # 5mm crop evapotranspiration
    pe = 2.0  # 2mm effective precipitation

    depletion, ks, ish = equations.soil_water_balance(prev_D=prev_D, etc=etc, Pe=pe)

    # Expected depletion = 10 - 2 + 5 = 13mm
    assert depletion == pytest.approx(13.0)
    assert ks == 1.0  # No stress

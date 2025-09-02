"""Core equations for the FAO-56 based water balance model."""

import math
import pandas as pd
from . import utils
from fastclime.core.logging import get_logger

log = get_logger(__name__)


def eto_penman_monteith(
    ts: "pd.Timestamp",
    lat: float,
    temp_c: float,
    rh_percent: float,
    wind_ms: float,
    solar_rad_w_m2: float,
    atmos_press_kpa: float,
) -> float:
    """
    Calculates Reference Evapotranspiration (ETo) using FAO-56 Penman-Monteith for an hourly step.

    Args:
        ts: Timestamp of the measurement.
        lat: Latitude in degrees.
        temp_c: Air temperature in Celsius.
        rh_percent: Relative humidity in percent.
        wind_ms: Wind speed in m/s.
        solar_rad_w_m2: Solar radiation in W/m2.
        atmos_press_kpa: Atmospheric pressure in kPa.

    Returns:
        ETo in mm/hour.
    """
    # Convert units and get time components
    lat_rad = math.radians(lat)
    day_of_year = utils.get_day_of_year(ts)
    hour = ts.hour
    solar_rad_mj_m2_h = solar_rad_w_m2 * 0.0036  # W/m2 to MJ/m2/h

    # --- Intermediate calculations ---
    # 1. Vapor Pressure
    es = utils.get_saturation_vapor_pressure(temp_c)
    ea = utils.get_actual_vapor_pressure(rh_percent, es)
    vpd = es - ea

    # 2. Key parameters
    delta = utils.get_delta_saturation_vapor_pressure(temp_c)
    gamma = utils.get_psychrometric_constant(atmos_press_kpa)

    # 3. Radiation
    solar_declination = utils.get_solar_declination(day_of_year)
    sunset_angle = utils.get_sunset_hour_angle(lat_rad, solar_declination)
    ra = utils.get_extraterrestrial_radiation_hourly(
        lat_rad, solar_declination, sunset_angle, day_of_year, hour
    )

    # Net radiation calculation requires daily min/max temps, which we don't have for hourly.
    # We will use a simplified approach for Rnl for now.
    # A more accurate implementation would need daily Tmin/Tmax.
    rns = utils.get_net_shortwave_radiation(solar_rad_mj_m2_h)

    # Simplified Rnl: assumes Tmin/Tmax are close to current temp
    t_k = temp_c + 273.16
    rnl = utils.get_net_longwave_radiation(t_k, t_k, ea, solar_rad_mj_m2_h, ra)

    rn = rns - rnl

    # 4. Soil Heat Flux
    is_daytime = solar_rad_mj_m2_h > 0
    g = utils.get_soil_heat_flux(rn, is_daytime)

    # --- Penman-Monteith Equation (Hourly, Eq. 53) ---
    numerator_rad = 0.408 * delta * (rn - g)
    numerator_aero = gamma * (37 / (temp_c + 273)) * wind_ms * vpd
    denominator = delta + gamma * (1 + 0.34 * wind_ms)

    eto = (numerator_rad + numerator_aero) / denominator
    return max(0, eto)


def etc(kc: float, eto: float) -> float:
    """Calculates Crop Evapotranspiration (ETc)."""
    return kc * eto


def soil_water_balance(
    prev_D: float, etc: float, Pe: float, irrigation_mm: float = 0
) -> tuple[float, float, float]:
    """
    Calculates the daily soil water balance. (Simplified for now)

    Returns:
        Tuple of (Depletion_at_end_of_day, Ks_stress_coeff, HWI_index)
    """
    # This is a simplified version. A full implementation would need soil properties.
    depletion = prev_D - Pe - irrigation_mm + etc

    # Placeholder for stress calculations
    ks = 1.0 if depletion >= 0 else 0.0
    hwi = depletion  # Placeholder

    return max(0, depletion), ks, hwi

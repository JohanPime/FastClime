"""Utility functions for the dynamic water balance model."""

import math
import numpy as np
import pandas as pd


def get_day_of_year(ts: pd.Timestamp) -> int:
    """Calculates the day of the year (1-366)."""
    return ts.dayofyear


def get_solar_declination(day_of_year: int) -> float:
    """Eq. 24: Solar declination (delta) in radians."""
    return 0.409 * math.sin(2 * math.pi / 365 * day_of_year - 1.39)


def get_sunset_hour_angle(latitude_rad: float, solar_declination_rad: float) -> float:
    """Eq. 25: Sunset hour angle (omega_s) in radians."""
    cos_omega_s = -math.tan(latitude_rad) * math.tan(solar_declination_rad)
    return math.acos(max(-1.0, min(1.0, cos_omega_s)))


def get_extraterrestrial_radiation_hourly(
    latitude_rad: float,
    solar_declination_rad: float,
    sunset_hour_angle_rad: float,
    day_of_year: int,
    hour: int,
) -> float:
    """Eq. 28: Extraterrestrial radiation for hourly periods (Ra) in MJ m-2 h-1."""
    # Solar constant
    Gsc = 0.0820  # MJ m-2 min-1
    # Inverse relative distance Earth-Sun
    dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * day_of_year)

    # Solar time angle at midpoint of period
    t = hour + 0.5
    omega = (math.pi / 12) * ((t - 12) - 0.5)  # Simplified, needs solar time correction

    omega_1 = omega - (math.pi / 24)
    omega_2 = omega + (math.pi / 24)

    # Clamp omega_1 and omega_2 to be within -sunset_hour_angle and +sunset_hour_angle
    omega_1 = max(-sunset_hour_angle_rad, min(omega_1, sunset_hour_angle_rad))
    omega_2 = max(-sunset_hour_angle_rad, min(omega_2, sunset_hour_angle_rad))

    term1 = (12 * 60 / math.pi) * Gsc * dr
    term2 = (
        (omega_2 - omega_1) * math.sin(latitude_rad) * math.sin(solar_declination_rad)
    )
    term3 = (
        math.cos(latitude_rad)
        * math.cos(solar_declination_rad)
        * (math.sin(omega_2) - math.sin(omega_1))
    )

    Ra = term1 * (term2 + term3)
    return max(0, Ra)


def get_saturation_vapor_pressure(temp_c: float) -> float:
    """Eq. 11: Saturation vapor pressure (e_s) in kPa."""
    return 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))


def get_actual_vapor_pressure(
    rh_percent: float, saturation_vapor_pressure_kpa: float
) -> float:
    """Eq. 17/54: Actual vapor pressure (e_a) in kPa."""
    return (rh_percent / 100) * saturation_vapor_pressure_kpa


def get_delta_saturation_vapor_pressure(temp_c: float) -> float:
    """Eq. 13: Slope of the saturation vapor pressure curve (Delta) in kPa/C."""
    numerator = 4098 * (0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3)))
    denominator = (temp_c + 237.3) ** 2
    return numerator / denominator


def get_psychrometric_constant(atmospheric_pressure_kpa: float) -> float:
    """Eq. 8: Psychrometric constant (gamma) in kPa/C."""
    return 0.000665 * atmospheric_pressure_kpa


def get_net_shortwave_radiation(
    solar_radiation_mj_m2_h: float, albedo: float = 0.23
) -> float:
    """Eq. 38: Net shortwave radiation (Rns) in MJ m-2 h-1."""
    return (1 - albedo) * solar_radiation_mj_m2_h


def get_net_longwave_radiation(
    t_max_k: float, t_min_k: float, ea_kpa: float, rs_mj_m2_h: float, ra_mj_m2_h: float
) -> float:
    """Eq. 39: Net longwave radiation (Rnl) in MJ m-2 h-1."""
    # Stefan-Boltzmann constant for hourly period
    sigma = 2.043e-10  # MJ K-4 m-2 h-1

    # Cloudiness factor
    if ra_mj_m2_h > 0:
        rso = (0.75) * ra_mj_m2_h  # Simplified Rso calculation
        cloudiness_factor = 1.35 * (rs_mj_m2_h / rso) - 0.35
    else:  # Nighttime
        cloudiness_factor = 0.7  # Assume some cloudiness

    cloudiness_factor = max(0.05, min(1.0, cloudiness_factor))

    term1 = sigma * ((t_max_k**4 + t_min_k**4) / 2)
    term2 = 0.34 - 0.14 * math.sqrt(ea_kpa)
    term3 = cloudiness_factor

    return term1 * term2 * term3


def get_soil_heat_flux(net_radiation_mj_m2_h: float, is_daytime: bool) -> float:
    """Eq. 45-46: Soil heat flux (G) in MJ m-2 h-1."""
    return (
        (0.1 * net_radiation_mj_m2_h) if is_daytime else (0.5 * net_radiation_mj_m2_h)
    )

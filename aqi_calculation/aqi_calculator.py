"""
U.S. EPA AQI Calculation using breakpoint interpolation.

This module calculates the Air Quality Index (AQI) on the 0–500 scale
using the U.S. EPA breakpoint methodology applied to individual pollutant
concentrations.

Breakpoint tables are sourced from:
    https://www.airnow.gov/aqi/aqi-basics/
    https://www.epa.gov/outdoor-air-quality-data/air-quality-index-reporting

Pollutant concentrations are expected in the units provided by the
OpenWeatherMap Air Pollution API (μg/m³ for all pollutants). Unit
conversions to the EPA standard units (ppm for CO, ppb for NO₂, O₃, SO₂)
are performed internally.

Reference AQI scale (U.S. EPA):
    0   –  50   Good
    51  – 100   Moderate
    101 – 150   Unhealthy for Sensitive Groups (USG)
    151 – 200   Unhealthy
    201 – 300   Very Unhealthy
    301 – 500   Hazardous
"""

from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────
#  EPA Breakpoint Tables
# ──────────────────────────────────────────────────────────────────────
# Each table is a list of (AQI_low, AQI_high, conc_low, conc_high) tuples.
# Breakpoints are inclusive on both ends per the EPA definition.

PM25_BREAKPOINTS: List[Tuple[int, int, float, float]] = [
    (0,   50,   0.0,   12.0),
    (51,  100,  12.1,  35.4),
    (101, 150,  35.5,  55.4),
    (151, 200,  55.5,  150.4),
    (201, 300,  150.5, 250.4),
    (301, 400,  250.5, 350.4),
    (401, 500,  350.5, 500.4),
]

PM10_BREAKPOINTS: List[Tuple[int, int, float, float]] = [
    (0,   50,   0.0,  54.0),
    (51,  100,  55.0, 154.0),
    (101, 150,  155.0, 254.0),
    (151, 200,  255.0, 354.0),
    (201, 300,  355.0, 424.0),
    (301, 400,  425.0, 504.0),
    (401, 500,  505.0, 604.0),
]

# CO breakpoints in ppm (OpenWeatherMap gives ug/m3 - conversion applied)
CO_BREAKPOINTS_PPM: List[Tuple[int, int, float, float]] = [
    (0,   50,   0.0,  4.4),
    (51,  100,  4.5,  9.4),
    (101, 150,  9.5,  12.4),
    (151, 200,  12.5, 15.4),
    (201, 300,  15.5, 30.4),
    (301, 400,  30.5, 40.4),
    (401, 500,  40.5, 50.4),
]

# NO2 breakpoints in ppb (OpenWeatherMap gives ug/m3 - conversion applied)
NO2_BREAKPOINTS_PPB: List[Tuple[int, int, float, float]] = [
    (0,   50,   0,    53),
    (51,  100,  54,   100),
    (101, 150,  101,  360),
    (151, 200,  361,  649),
    (201, 300,  650,  1249),
    (301, 400,  1250, 1649),
    (401, 500,  1650, 2049),
]

# O3 breakpoints in ppb (8-hr, OpenWeatherMap gives ug/m3 - conversion applied)
O3_BREAKPOINTS_PPB: List[Tuple[int, int, float, float]] = [
    (0,   50,   0,   54),
    (51,  100,  55,  70),
    (101, 150,  71,  85),
    (151, 200,  86,  105),
    (201, 300,  106, 200),
]

# SO2 breakpoints in ppb (1-hr, OpenWeatherMap gives ug/m3 - conversion applied)
SO2_BREAKPOINTS_PPB: List[Tuple[int, int, float, float]] = [
    (0,   50,   0,    35),
    (51,  100,  36,   75),
    (101, 150,  76,   185),
    (151, 200,  186,  304),
    (201, 300,  305,  604),
    (301, 400,  605,  804),
    (401, 500,  805,  1004),
]

# ──────────────────────────────────────────────────────────────────────
#  Unit Conversion Constants
# ──────────────────────────────────────────────────────────────────────
# Conversion from μg/m³ to EPA units at 25 °C, 1 atm.
# Molar volume of air = 24.45 L/mol

MOLAR_VOLUME = 24.45  # L/mol at 25 °C, 1 atm

MW_CO  = 28.01   # g/mol
MW_NO2 = 46.01   # g/mol
MW_O3  = 48.00   # g/mol
MW_SO2 = 64.06   # g/mol


def _ugm3_to_ppm(ugm3: float, mw: float) -> float:
    """Convert μg/m³ to ppm."""
    return ugm3 * MOLAR_VOLUME / (mw * 1000)


def _ugm3_to_ppb(ugm3: float, mw: float) -> float:
    """Convert μg/m³ to ppb."""
    return ugm3 * MOLAR_VOLUME / mw


# ──────────────────────────────────────────────────────────────────────
#  Sub-Index Calculation
# ──────────────────────────────────────────────────────────────────────

def _calculate_sub_index(concentration: float, breakpoints: List[Tuple[int, int, float, float]]) -> Optional[float]:
    """Calculate AQI sub-index for a given concentration using EPA breakpoints.

    Args:
        concentration: Pollutant concentration in the EPA breakpoint unit
                       (μg/m³ for PM2.5/PM10, ppm for CO, ppb for NO₂/O₃/SO₂).
        breakpoints: EPA breakpoint table for this pollutant.

    Returns:
        AQI sub-index as a float, or None if concentration is below the
        lowest breakpoint lower bound.
    """
    if concentration < 0:
        return 0.0

    for aqi_lo, aqi_hi, c_lo, c_hi in breakpoints:
        if c_lo <= concentration <= c_hi:
            return ((aqi_hi - aqi_lo) / (c_hi - c_lo)) * (concentration - c_lo) + aqi_lo

    # If concentration exceeds all breakpoints, cap at AQI 500
    last = breakpoints[-1]
    if concentration > last[3]:
        return float(last[1])  # AQI 500

    return None


# ──────────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────────

def get_all_sub_indices(pm2_5: float, pm10: float, co: float,
                        no2: float, o3: float, so2: float) -> Dict[str, float]:
    """Calculate AQI sub-indices for all six criteria pollutants.

    All inputs are in μg/m³ (the unit returned by the OpenWeatherMap API).
    Unit conversions are performed internally.

    Returns:
        Dict mapping pollutant name to its AQI sub-index (float).
    """
    return {
        'pm2_5': _calculate_sub_index(pm2_5, PM25_BREAKPOINTS),
        'pm10': _calculate_sub_index(pm10, PM10_BREAKPOINTS),
        'co': _calculate_sub_index(_ugm3_to_ppm(co, MW_CO), CO_BREAKPOINTS_PPM),
        'no2': _calculate_sub_index(_ugm3_to_ppb(no2, MW_NO2), NO2_BREAKPOINTS_PPB),
        'o3': _calculate_sub_index(_ugm3_to_ppb(o3, MW_O3), O3_BREAKPOINTS_PPB),
        'so2': _calculate_sub_index(_ugm3_to_ppb(so2, MW_SO2), SO2_BREAKPOINTS_PPB),
    }


def calculate_aqi(pm2_5: float, pm10: float, co: float,
                  no2: float, o3: float, so2: float) -> Tuple[int, str]:
    """Calculate the overall AQI and the primary (dominant) pollutant.

    All inputs are in μg/m³ (the unit returned by the OpenWeatherMap API).

    The overall AQI is the maximum of the individual pollutant sub-indices,
    per the U.S. EPA definition.

    Returns:
        (aqi, primary_pollutant) where aqi is an integer 0–500 and
        primary_pollutant is one of: 'pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2'.
    """
    sub_indices = get_all_sub_indices(pm2_5, pm10, co, no2, o3, so2)

    # Find the pollutant with the highest sub-index
    primary_pollutant = max(sub_indices, key=lambda k: sub_indices[k] or 0)
    aqi_value = sub_indices[primary_pollutant]

    if aqi_value is None:
        return 0, 'pm2_5'  # fallback

    return int(round(aqi_value)), primary_pollutant


def get_aqi_category(aqi: int) -> str:
    """Return the EPA AQI category name for a given AQI value.

    Categories:
        0–50   Good
        51–100 Moderate
        101–150 Unhealthy for Sensitive Groups
        151–200 Unhealthy
        201–300 Very Unhealthy
        301–500 Hazardous
    """
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Moderate'
    elif aqi <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi <= 200:
        return 'Unhealthy'
    elif aqi <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'


def get_aqi_color(aqi: int) -> str:
    """Return the standard EPA hex color for a given AQI value."""
    if aqi <= 50:
        return '#00E400'   # Green
    elif aqi <= 100:
        return '#FFFF00'   # Yellow
    elif aqi <= 150:
        return '#FF7E00'   # Orange
    elif aqi <= 200:
        return '#FF0000'   # Red
    elif aqi <= 300:
        return '#8F3F97'   # Purple
    else:
        return '#7E0023'   # Maroon

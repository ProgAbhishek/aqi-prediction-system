# AQI Calculation Methodology

## Overview

This project calculates the Air Quality Index (AQI) using the **U.S. EPA breakpoint interpolation method**, producing values on the standard **0–500 scale**. The OpenWeatherMap Air Pollution API provides raw pollutant concentrations, which are converted and processed through EPA breakpoint tables to yield scientifically accurate AQI values.

## U.S. EPA AQI Scale

| AQI Range | Category | Health Implications |
|-----------|----------|-------------------|
| 0–50 | Good | Air quality is satisfactory; little or no risk |
| 51–100 | Moderate | Acceptable; sensitive individuals may be affected |
| 101–150 | Unhealthy for Sensitive Groups | Sensitive groups may experience health effects |
| 151–200 | Unhealthy | Everyone may begin to experience health effects |
| 201–300 | Very Unhealthy | Health alert: everyone may experience serious effects |
| 301–500 | Hazardous | Health emergency for the entire population |

## AQI Calculation Formula

For each pollutant, a sub-index is calculated using the EPA breakpoint interpolation formula:

```
AQI = ((AQI_high - AQI_low) / (BP_high - BP_low)) × (C - BP_low) + AQI_low
```

Where:
- `C` = measured concentration of the pollutant
- `BP_high` and `BP_low` = the breakpoint concentrations that bracket `C`
- `AQI_high` and `AQI_low` = the AQI values corresponding to those breakpoints

The **overall AQI** is the **maximum** of the individual sub-indices across all six criteria pollutants.

## Pollutants and Breakpoint Tables

### PM2.5 (μg/m³, 24-hour)

| AQI Low | AQI High | PM2.5 Low (μg/m³) | PM2.5 High (μg/m³) |
|---------|----------|-------------------|---------------------|
| 0 | 50 | 0.0 | 12.0 |
| 51 | 100 | 12.1 | 35.4 |
| 101 | 150 | 35.5 | 55.4 |
| 151 | 200 | 55.5 | 150.4 |
| 201 | 300 | 150.5 | 250.4 |
| 301 | 400 | 250.5 | 350.4 |
| 401 | 500 | 350.5 | 500.4 |

### PM10 (μg/m³, 24-hour)

| AQI Low | AQI High | PM10 Low (μg/m³) | PM10 High (μg/m³) |
|---------|----------|------------------|---------------------|
| 0 | 50 | 0 | 54 |
| 51 | 100 | 55 | 154 |
| 101 | 150 | 155 | 254 |
| 151 | 200 | 255 | 354 |
| 201 | 300 | 355 | 424 |
| 301 | 400 | 425 | 504 |
| 401 | 500 | 505 | 604 |

### CO (ppm, 8-hour)

| AQI Low | AQI High | CO Low (ppm) | CO High (ppm) |
|---------|----------|-------------|---------------|
| 0 | 50 | 0.0 | 4.4 |
| 51 | 100 | 4.5 | 9.4 |
| 101 | 150 | 9.5 | 12.4 |
| 151 | 200 | 12.5 | 15.4 |
| 201 | 300 | 15.5 | 30.4 |
| 301 | 400 | 30.5 | 40.4 |
| 401 | 500 | 40.5 | 50.4 |

### NO₂ (ppb, 1-hour)

| AQI Low | AQI High | NO₂ Low (ppb) | NO₂ High (ppb) |
|---------|----------|--------------|----------------|
| 0 | 50 | 0 | 53 |
| 51 | 100 | 54 | 100 |
| 101 | 150 | 101 | 360 |
| 151 | 200 | 361 | 649 |
| 201 | 300 | 650 | 1249 |
| 301 | 400 | 1250 | 1649 |
| 401 | 500 | 1650 | 2049 |

### O₃ (ppb, 8-hour)

| AQI Low | AQI High | O₃ Low (ppb) | O₃ High (ppb) |
|---------|----------|-------------|---------------|
| 0 | 50 | 0 | 54 |
| 51 | 100 | 55 | 70 |
| 101 | 150 | 71 | 85 |
| 151 | 200 | 86 | 105 |
| 201 | 300 | 106 | 200 |

### SO₂ (ppb, 1-hour)

| AQI Low | AQI High | SO₂ Low (ppb) | SO₂ High (ppb) |
|---------|----------|--------------|----------------|
| 0 | 50 | 0 | 35 |
| 51 | 100 | 36 | 75 |
| 101 | 150 | 76 | 185 |
| 151 | 200 | 186 | 304 |
| 201 | 300 | 305 | 604 |
| 301 | 400 | 605 | 804 |
| 401 | 500 | 805 | 1004 |

## Unit Conversions

The OpenWeatherMap API provides all pollutant concentrations in **μg/m³**. The EPA breakpoint tables use different units for some pollutants. Conversions are performed at **25°C and 1 atm** (molar volume = 24.45 L/mol).

| Pollutant | API Unit | EPA Unit | Molecular Weight | Conversion Formula |
|-----------|----------|----------|-----------------|-------------------|
| PM2.5 | μg/m³ | μg/m³ | — | None needed |
| PM10 | μg/m³ | μg/m³ | — | None needed |
| CO | μg/m³ | ppm | 28.01 g/mol | ppm = μg/m³ × 24.45 / 28,010 |
| NO₂ | μg/m³ | ppb | 46.01 g/mol | ppb = μg/m³ × 24.45 / 46.01 |
| O₃ | μg/m³ | ppb | 48.00 g/mol | ppb = μg/m³ × 24.45 / 48.00 |
| SO₂ | μg/m³ | ppb | 64.06 g/mol | ppb = μg/m³ × 24.45 / 64.06 |

## Implementation

The AQI calculator is implemented in `aqi_calculation/aqi_calculator.py` and provides:

- `calculate_aqi(pm2_5, pm10, co, no2, o3, so2)` → `(aqi: int, primary_pollutant: str)`
- `get_all_sub_indices(pm2_5, pm10, co, no2, o3, so2)` → `dict[str, float]`
- `get_aqi_category(aqi)` → `str`
- `get_aqi_color(aqi)` → `str` (hex color)

## Limitations

1. **O₃ breakpoints**: Uses the 8-hour O₃ breakpoints for AQI 0–200. For AQI > 200, the EPA uses 1-hour O₃ breakpoints, which are also implemented.
2. **Instantaneous readings**: The API provides instantaneous concentrations, not 24-hour or 8-hour averages as specified by the EPA. This is an approximation for a real-time monitoring system.
3. **Temperature/pressure**: Unit conversions assume standard conditions (25°C, 1 atm). Actual conditions in Kathmandu may vary slightly.

## References

- [U.S. EPA AQI Basics](https://www.airnow.gov/aqi/aqi-basics/)
- [EPA AQI Reporting Technical Documentation](https://www.epa.gov/outdoor-air-quality-data/air-quality-index-reporting)
- [OpenWeatherMap Air Pollution API](https://openweathermap.org/api/air-pollution)

"""Tests for the AQI Calculator module.

Run with:
    venv/Scripts/python -m pytest tests/test_aqi_calculator.py -v
"""

import sys
import os

# Ensure the project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from aqi_calculation.aqi_calculator import (
    calculate_aqi,
    get_aqi_category,
    get_aqi_color,
    get_all_sub_indices,
    _ugm3_to_ppm,
    _ugm3_to_ppb,
    MW_CO,
    MW_NO2,
    MW_O3,
    MW_SO2,
    MOLAR_VOLUME,
)


class TestUnitConversions:
    """Test unit conversion functions."""

    def test_co_conversion(self):
        # 4401 μg/m³ should equal ~3.85 ppm (below breakpoint 4.4)
        ppm = _ugm3_to_ppm(4401, MW_CO)
        assert abs(ppm - 3.85) < 0.01

    def test_no2_conversion(self):
        # 100 μg/m³ should equal ~53.1 ppb
        ppb = _ugm3_to_ppb(100, MW_NO2)
        assert abs(ppb - 53.1) < 0.1

    def test_o3_conversion(self):
        # 100 μg/m³ should equal ~50.9 ppb
        ppb = _ugm3_to_ppb(100, MW_O3)
        assert abs(ppb - 50.9) < 0.1

    def test_so2_conversion(self):
        # 100 μg/m³ should equal ~38.2 ppb
        ppb = _ugm3_to_ppb(100, MW_SO2)
        assert abs(ppb - 38.2) < 0.1


class TestSubIndices:
    """Test individual pollutant sub-index calculations."""

    def test_pm2_5_zero(self):
        subs = get_all_sub_indices(0, 0, 0, 0, 0, 0)
        assert subs['pm2_5'] == 0.0

    def test_pm2_5_good(self):
        # PM2.5 = 10 μg/m³ → AQI ~42 (Good)
        subs = get_all_sub_indices(10, 0, 0, 0, 0, 0)
        assert 0 <= subs['pm2_5'] <= 50

    def test_pm2_5_moderate(self):
        # PM2.5 = 25 μg/m³ → AQI ~81 (Moderate)
        subs = get_all_sub_indices(25, 0, 0, 0, 0, 0)
        assert 51 <= subs['pm2_5'] <= 100

    def test_pm2_5_usg(self):
        # PM2.5 = 45 μg/m³ → AQI ~126 (USG)
        subs = get_all_sub_indices(45, 0, 0, 0, 0, 0)
        assert 101 <= subs['pm2_5'] <= 150

    def test_pm2_5_unhealthy(self):
        # PM2.5 = 100 μg/m³ → AQI ~162 (Unhealthy)
        subs = get_all_sub_indices(100, 0, 0, 0, 0, 0)
        assert 151 <= subs['pm2_5'] <= 200

    def test_pm2_5_very_unhealthy(self):
        # PM2.5 = 200 μg/m³ → AQI ~253 (Very Unhealthy)
        subs = get_all_sub_indices(200, 0, 0, 0, 0, 0)
        assert 201 <= subs['pm2_5'] <= 300

    def test_pm2_5_hazardous(self):
        # PM2.5 = 400 μg/m³ → AQI ~435 (Hazardous)
        subs = get_all_sub_indices(400, 0, 0, 0, 0, 0)
        assert 301 <= subs['pm2_5'] <= 500

    def test_pm10_good(self):
        # PM10 = 30 μg/m³ → AQI ~28 (Good)
        subs = get_all_sub_indices(0, 30, 0, 0, 0, 0)
        assert 0 <= subs['pm10'] <= 50

    def test_pm10_moderate(self):
        # PM10 = 100 μg/m³ → AQI ~65 (Moderate)
        subs = get_all_sub_indices(0, 100, 0, 0, 0, 0)
        assert 51 <= subs['pm10'] <= 100


class TestOverallAQI:
    """Test the overall AQI calculation."""

    def test_zero_pollutants(self):
        aqi, primary = calculate_aqi(0, 0, 0, 0, 0, 0)
        assert aqi == 0
        assert primary in ['pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2']

    def test_typical_kathmandu(self):
        # Typical Kathmandu values
        aqi, primary = calculate_aqi(29.64, 31.84, 296.88, 4.47, 93.53, 4.63)
        assert 50 <= aqi <= 150  # Should be Moderate or USG
        assert primary == 'pm2_5'  # PM2.5 usually dominates

    def test_high_pm2_5(self):
        # Very high PM2.5
        aqi, primary = calculate_aqi(200, 100, 500, 10, 50, 5)
        assert aqi >= 200
        assert primary == 'pm2_5'

    def test_result_is_integer(self):
        aqi, _ = calculate_aqi(25.3, 40.7, 500.2, 8.5, 60.1, 3.2)
        assert isinstance(aqi, int)

    def test_result_in_range(self):
        # All zero should give 0
        aqi, _ = calculate_aqi(0, 0, 0, 0, 0, 0)
        assert 0 <= aqi <= 500

    def test_extreme_values(self):
        # Very extreme values should cap at 500
        aqi, _ = calculate_aqi(1000, 1000, 10000, 5000, 500, 500)
        assert aqi == 500


class TestAQICategory:
    """Test AQI category classification."""

    def test_good(self):
        assert get_aqi_category(0) == 'Good'
        assert get_aqi_category(25) == 'Good'
        assert get_aqi_category(50) == 'Good'

    def test_moderate(self):
        assert get_aqi_category(51) == 'Moderate'
        assert get_aqi_category(75) == 'Moderate'
        assert get_aqi_category(100) == 'Moderate'

    def test_usg(self):
        assert get_aqi_category(101) == 'Unhealthy for Sensitive Groups'
        assert get_aqi_category(125) == 'Unhealthy for Sensitive Groups'
        assert get_aqi_category(150) == 'Unhealthy for Sensitive Groups'

    def test_unhealthy(self):
        assert get_aqi_category(151) == 'Unhealthy'
        assert get_aqi_category(175) == 'Unhealthy'
        assert get_aqi_category(200) == 'Unhealthy'

    def test_very_unhealthy(self):
        assert get_aqi_category(201) == 'Very Unhealthy'
        assert get_aqi_category(250) == 'Very Unhealthy'
        assert get_aqi_category(300) == 'Very Unhealthy'

    def test_hazardous(self):
        assert get_aqi_category(301) == 'Hazardous'
        assert get_aqi_category(400) == 'Hazardous'
        assert get_aqi_category(500) == 'Hazardous'


class TestAQIColor:
    """Test AQI color mapping."""

    def test_good_green(self):
        assert get_aqi_color(25) == '#00E400'

    def test_moderate_yellow(self):
        assert get_aqi_color(75) == '#FFFF00'

    def test_usg_orange(self):
        assert get_aqi_color(125) == '#FF7E00'

    def test_unhealthy_red(self):
        assert get_aqi_color(175) == '#FF0000'

    def test_very_unhealthy_purple(self):
        assert get_aqi_color(250) == '#8F3F97'

    def test_hazardous_maroon(self):
        assert get_aqi_color(400) == '#7E0023'

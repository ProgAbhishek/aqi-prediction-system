"""Service layer for reading air-quality data for the Django dashboard.

The data-collection pipeline owns this database (database/air_quality.db).
Django only reads from it — it never writes to or migrates the schema.
"""

import sqlite3
from pathlib import Path

from django.conf import settings

AIR_QUALITY_DB_PATH = Path(settings.BASE_DIR) / 'database' / 'air_quality.db'


# ─────────────────────────────────────────────────────────────
#  Centralized AQI Classification (U.S. EPA 0–500 scale)
# ─────────────────────────────────────────────────────────────

AQI_INFO = {
    'good': {
        'range': (0, 50),
        'category': 'Good',
        'meaning': 'Air quality is satisfactory, and air pollution poses little or no risk.',
        'css_class': 'aqi-good',
        'color': '#00E400',
        'icon': '😊',
        'health_recommendation': (
            'Air quality is satisfactory and poses little or no risk. '
            'Ideal for all outdoor activities.'
        ),
        'suggestions': [
            'Outdoor activities are fully suitable.',
            'No health risk from current air quality.',
        ],
    },
    'moderate': {
        'range': (51, 100),
        'category': 'Moderate',
        'meaning': 'Air quality is acceptable, but some pollutants may concern sensitive individuals.',
        'css_class': 'aqi-moderate',
        'color': '#FFFF00',
        'icon': '🙂',
        'health_recommendation': (
            'Air quality is acceptable. Unusually sensitive people should '
            'consider reducing prolonged outdoor exertion.'
        ),
        'suggestions': [
            'Generally acceptable for most people.',
            'Sensitive individuals may consider limiting prolonged outdoor exertion.',
        ],
    },
    'usg': {
        'range': (101, 150),
        'category': 'Unhealthy for Sensitive Groups',
        'meaning': 'Members of sensitive groups may experience health effects.',
        'css_class': 'aqi-usg',
        'color': '#FF7E00',
        'icon': '😐',
        'health_recommendation': (
            'Sensitive groups (children, elderly, people with lung disease or '
            'heart disease) should reduce prolonged outdoor exertion. '
            'General public is less likely to be affected.'
        ),
        'suggestions': [
            'Sensitive groups should limit prolonged outdoor exertion.',
            'General public: enjoy outdoor activities, but pay attention.',
            'Consider checking air quality before outdoor exercise.',
        ],
    },
    'unhealthy': {
        'range': (151, 200),
        'category': 'Unhealthy',
        'meaning': 'Everyone may begin to experience health effects.',
        'css_class': 'aqi-unhealthy',
        'color': '#FF0000',
        'icon': '😷',
        'health_recommendation': (
            'Everyone should reduce prolonged outdoor exertion. '
            'Sensitive groups should avoid outdoor exertion entirely.'
        ),
        'suggestions': [
            'Everyone should limit prolonged outdoor exposure.',
            'Sensitive groups should avoid outdoor exertion.',
            'Consider indoor activities when possible.',
        ],
    },
    'very_unhealthy': {
        'range': (201, 300),
        'category': 'Very Unhealthy',
        'meaning': 'Health alert: everyone may experience more serious health effects.',
        'css_class': 'aqi-very-unhealthy',
        'color': '#8F3F97',
        'icon': '🤢',
        'health_recommendation': (
            'Health alert: everyone may experience serious health effects. '
            'Avoid all outdoor exertion. Keep windows closed.'
        ),
        'suggestions': [
            'Avoid all outdoor physical activities.',
            'Keep windows and doors closed.',
            'Use air purifiers indoors if available.',
            'Monitor air quality updates regularly.',
        ],
    },
    'hazardous': {
        'range': (301, 500),
        'category': 'Hazardous',
        'meaning': 'Health emergency: the entire population is affected.',
        'css_class': 'aqi-hazardous',
        'color': '#7E0023',
        'icon': '☠',
        'health_recommendation': (
            'Health emergency! The entire population is likely to be affected. '
            'Stay indoors, keep all windows closed, and avoid all outdoor activity.'
        ),
        'suggestions': [
            'Stay indoors with windows and doors closed.',
            'Avoid ALL outdoor activities.',
            'Use air purification systems at maximum capacity.',
            'Seek medical attention if experiencing symptoms.',
            'Monitor emergency broadcasts for updates.',
        ],
    },
}

# Ordered list for range lookup
_AQI_RANGES = [
    ('good', 0, 50),
    ('moderate', 51, 100),
    ('usg', 101, 150),
    ('unhealthy', 151, 200),
    ('very_unhealthy', 201, 300),
    ('hazardous', 301, 500),
]

_AQI_KEYS_BY_NAME = {k: k for k in ['good', 'moderate', 'usg', 'unhealthy', 'very_unhealthy', 'hazardous']}

# Fallback for any unexpected AQI value
_AQI_FALLBACK = {
    'value': None,
    'category': 'Unknown',
    'meaning': 'Air quality data is unavailable.',
    'css_class': 'aqi-unknown',
    'color': '#666666',
    'icon': '❓',
    'health_recommendation': 'No recommendation available.',
    'suggestions': [],
}

# Pollutant metadata for display cards
POLLUTANT_INFO = {
    'pm2_5': {
        'label': 'PM2.5',
        'unit': 'μg/m³',
        'description': 'Fine particulate matter',
    },
    'pm10': {
        'label': 'PM10',
        'unit': 'μg/m³',
        'description': 'Coarse particulate matter',
    },
    'co': {
        'label': 'CO',
        'unit': 'μg/m³',
        'description': 'Carbon monoxide',
    },
    'no2': {
        'label': 'NO₂',
        'unit': 'μg/m³',
        'description': 'Nitrogen dioxide',
    },
    'o3': {
        'label': 'O₃',
        'unit': 'μg/m³',
        'description': 'Ozone',
    },
    'so2': {
        'label': 'SO₂',
        'unit': 'μg/m³',
        'description': 'Sulfur dioxide',
    },
}


def get_aqi_info(aqi):
    """Return the full AQI classification dict for a given AQI value (0–500).

    Returns a dict with: value, category, meaning, css_class, color,
    icon, health_recommendation, suggestions.
    """
    if aqi is None:
        return dict(_AQI_FALLBACK)
    aqi = int(aqi)
    for key, lo, hi in _AQI_RANGES:
        if lo <= aqi <= hi:
            info = dict(AQI_INFO[key])
            info['value'] = aqi
            return info
    # Above 500
    if aqi > 500:
        info = dict(AQI_INFO['hazardous'])
        info['value'] = aqi
        return info
    return dict(_AQI_FALLBACK)


def get_aqi_category(aqi):
    """Return the category string for a given AQI value."""
    return get_aqi_info(aqi)['category']


def get_health_recommendation(aqi):
    """Return the health recommendation string for a given AQI value."""
    return get_aqi_info(aqi)['health_recommendation']


def get_aqi_color_class(aqi):
    """Return the CSS class name for a given AQI value."""
    return get_aqi_info(aqi)['css_class']


def get_aqi_suggestions(aqi):
    """Return the list of suggestion strings for a given AQI value."""
    return get_aqi_info(aqi)['suggestions']


def compare_aqi(current_aqi, predicted_aqi):
    """Compare current and predicted AQI and return a comparison dict.

    Returns {'text': str, 'icon': str, 'css_class': str} describing
    whether air quality may worsen, improve, or stay similar.
    """
    if current_aqi is None or predicted_aqi is None:
        return {
            'text': 'Comparison unavailable.',
            'icon': '—',
            'css_class': 'comparison-neutral',
        }
    diff = predicted_aqi - current_aqi
    if diff > 10:
        return {
            'text': 'Air quality may worsen.',
            'icon': '⚠',
            'css_class': 'comparison-worse',
        }
    if diff < -10:
        return {
            'text': 'Air quality may improve.',
            'icon': '✓',
            'css_class': 'comparison-better',
        }
    return {
        'text': 'Air quality is expected to remain similar.',
        'icon': '—',
        'css_class': 'comparison-neutral',
    }


def get_pollutants(reading):
    """Build a list of pollutant display dicts from a reading.

    Each dict contains: key, label, value, unit, description.
    """
    pollutants = []
    for key, meta in POLLUTANT_INFO.items():
        pollutants.append({
            'key': key,
            'label': meta['label'],
            'value': reading.get(key),
            'unit': meta['unit'],
            'description': meta['description'],
        })
    return pollutants


# ─────────────────────────────────────────────────────────────
#  Database Access
# ─────────────────────────────────────────────────────────────

def _connect():
    """Open a read-only connection to the air quality database."""
    conn = sqlite3.connect(f'file:{AIR_QUALITY_DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_reading():
    """Return the most recent air_quality record as a dict, or None.

    The returned dict is enriched with full AQI classification info
    based on the calculated EPA AQI (0–500 scale).
    """
    try:
        conn = _connect()
        try:
            row = conn.execute(
                'SELECT * FROM air_quality ORDER BY id DESC LIMIT 1'
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return None

    if row is None:
        return None

    reading = dict(row)
    calc_aqi = reading.get('calculated_aqi')
    aqi_info = get_aqi_info(calc_aqi)
    reading['aqi_label'] = aqi_info['category']
    reading['aqi_color'] = aqi_info['color']
    reading['aqi_css_class'] = aqi_info['css_class']
    reading['aqi_meaning'] = aqi_info['meaning']
    reading['aqi_icon'] = aqi_info['icon']
    reading['aqi_recommendation'] = aqi_info['health_recommendation']
    reading['aqi_suggestions'] = aqi_info['suggestions']
    return reading


def count_records():
    """Return the total number of air_quality records, or 0 on failure."""
    try:
        conn = _connect()
        try:
            return conn.execute(
                'SELECT COUNT(*) AS total FROM air_quality'
            ).fetchone()['total']
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def get_recent_readings(limit=10):
    """Return the most recent air_quality records as a list of dicts."""
    try:
        conn = _connect()
        try:
            rows = conn.execute(
                'SELECT * FROM air_quality ORDER BY id DESC LIMIT ?', (limit,)
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []

    return [dict(row) for row in rows]


def get_historical_data(limit=200):
    """Return recent records ordered chronologically for chart rendering.

    Returns a list of dicts with keys: timestamp, aqi, pm2_5.
    Ordered oldest-first (ASC) so charts draw left-to-right in time.
    """
    try:
        conn = _connect()
        try:
            rows = conn.execute(
                'SELECT timestamp, calculated_aqi, aqi, pm2_5 '
                'FROM air_quality ORDER BY id DESC LIMIT ?', (limit,)
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []

    # Reverse so oldest comes first (charts draw left → right in time)
    result = []
    for row in reversed(rows):
        d = dict(row)
        # Use calculated_aqi as the display AQI; fall back to api aqi
        d['aqi'] = d.pop('calculated_aqi') or d.pop('aqi')
        result.append(d)
    return result

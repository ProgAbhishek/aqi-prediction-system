"""Service layer for reading air-quality data for the Django dashboard.

The data-collection pipeline owns this database (database/air_quality.db).
Django only reads from it — it never writes to or migrates the schema.
"""

import sqlite3
from pathlib import Path

from django.conf import settings

AIR_QUALITY_DB_PATH = Path(settings.BASE_DIR) / 'database' / 'air_quality.db'


# ─────────────────────────────────────────────────────────────
#  Centralized AQI Classification
# ─────────────────────────────────────────────────────────────

AQI_INFO = {
    1: {
        'value': 1,
        'category': 'Good',
        'meaning': 'Air quality is good.',
        'css_class': 'aqi-good',
        'color': '#2E7D32',
        'icon': '😊',
        'health_recommendation': (
            'Air quality is suitable for normal outdoor activities.'
        ),
        'suggestions': [
            'Outdoor activities are generally suitable.',
            'Normal daily activities can continue.',
        ],
    },
    2: {
        'value': 2,
        'category': 'Fair',
        'meaning': 'Air quality is acceptable.',
        'css_class': 'aqi-fair',
        'color': '#9E9D24',
        'icon': '🙂',
        'health_recommendation': (
            'Most people can continue normal outdoor activities. '
            'Sensitive individuals should monitor their symptoms.'
        ),
        'suggestions': [
            'Normal outdoor activities are generally acceptable.',
            'Sensitive individuals may monitor air quality.',
        ],
    },
    3: {
        'value': 3,
        'category': 'Moderate',
        'meaning': 'Some pollution is present.',
        'css_class': 'aqi-moderate',
        'color': '#EF6C00',
        'icon': '😐',
        'health_recommendation': (
            'Sensitive individuals should consider reducing '
            'prolonged outdoor activities.'
        ),
        'suggestions': [
            'Consider limiting prolonged outdoor activities.',
            'Sensitive individuals should take extra care.',
            'Consider checking air quality before outdoor exercise.',
        ],
    },
    4: {
        'value': 4,
        'category': 'Poor',
        'meaning': 'Air quality is unhealthy.',
        'css_class': 'aqi-poor',
        'color': '#C62828',
        'icon': '😷',
        'health_recommendation': (
            'Consider reducing prolonged outdoor activities, '
            'especially for sensitive individuals.'
        ),
        'suggestions': [
            'Reduce prolonged outdoor exposure.',
            'Consider indoor activities when possible.',
            'Sensitive individuals should take extra precautions.',
        ],
    },
    5: {
        'value': 5,
        'category': 'Very Poor',
        'meaning': 'Air quality is very unhealthy.',
        'css_class': 'aqi-very-poor',
        'color': '#8E0000',
        'icon': '🤢',
        'health_recommendation': (
            'Avoid or reduce outdoor activities, particularly '
            'for sensitive individuals.'
        ),
        'suggestions': [
            'Avoid prolonged outdoor exposure.',
            'Consider staying indoors when possible.',
            'Monitor air quality updates regularly.',
        ],
    },
}

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
    """Return the full AQI classification dict for a given AQI value.

    Returns a dict with: value, category, meaning, css_class, color,
    icon, health_recommendation, suggestions.
    """
    if aqi is None:
        return dict(_AQI_FALLBACK)
    # Clamp to 1–5 range for safety
    clamped = max(1, min(5, int(aqi)))
    info = dict(AQI_INFO.get(clamped, _AQI_FALLBACK))
    info['value'] = int(aqi)
    return info


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
    if predicted_aqi > current_aqi:
        return {
            'text': 'Air quality may worsen.',
            'icon': '⚠',
            'css_class': 'comparison-worse',
        }
    if predicted_aqi < current_aqi:
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

    The returned dict is enriched with full AQI classification info.
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
    aqi_info = get_aqi_info(reading.get('aqi'))
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
                'SELECT timestamp, aqi, pm2_5 '
                'FROM air_quality ORDER BY id DESC LIMIT ?', (limit,)
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []

    # Reverse so oldest comes first (charts draw left → right in time)
    return [dict(row) for row in reversed(rows)]

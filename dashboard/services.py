"""Service layer for reading air-quality data for the Django dashboard.

The data-collection pipeline owns this database (database/air_quality.db).
Django only reads from it — it never writes to or migrates the schema.
"""

import sqlite3
from pathlib import Path

from django.conf import settings

AIR_QUALITY_DB_PATH = Path(settings.BASE_DIR) / 'database' / 'air_quality.db'

# OpenWeatherMap AQI scale (1-5) -> (label, color)
AQI_LEVELS = {
    1: ('Good', '#4caf50'),
    2: ('Fair', '#8bc34a'),
    3: ('Moderate', '#ff9800'),
    4: ('Poor', '#f44336'),
    5: ('Very Poor', '#9c27b0'),
}


def _connect():
    """Open a read-only connection to the air quality database."""
    conn = sqlite3.connect(f'file:{AIR_QUALITY_DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_reading():
    """Return the most recent air_quality record as a dict, or None."""
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
    label, color = AQI_LEVELS.get(reading.get('aqi'), ('Unknown', '#666'))
    reading['aqi_label'] = label
    reading['aqi_color'] = color
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

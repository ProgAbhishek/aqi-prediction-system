"""Service layer for ML model loading and prediction for the Django dashboard.

Loads trained models from ML/saved_models/. Models predict on the U.S. EPA
AQI (0–500) scale calculated via breakpoint interpolation.

The prediction input is built from the trained model's own
feature_names_in_ attribute, so feature names and order always match training.
"""

import warnings
import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
from django.conf import settings

RANDOM_FOREST_PATH = Path(settings.BASE_DIR) / 'ML' / 'saved_models' / 'random_forest_aqi_500.pkl'
ISOLATION_FOREST_PATH = Path(settings.BASE_DIR) / 'ML' / 'saved_models' / 'isolation_forest_aqi_500.pkl'

_rf_model = None
_rf_error = None
_if_model = None
_if_error = None


def _load_random_forest():
    """Load and cache the Random Forest model. Returns the model or None."""
    global _rf_model, _rf_error
    if _rf_model is not None or _rf_error is not None:
        return _rf_model

    try:
        import joblib
        from sklearn.exceptions import InconsistentVersionWarning
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InconsistentVersionWarning)
            _rf_model = joblib.load(str(RANDOM_FOREST_PATH))
    except Exception as exc:
        _rf_error = str(exc)
        _rf_model = None
    return _rf_model


def _load_isolation_forest():
    """Load and cache the Isolation Forest model. Returns the model or None."""
    global _if_model, _if_error
    if _if_model is not None or _if_error is not None:
        return _if_model

    try:
        import joblib
        from sklearn.exceptions import InconsistentVersionWarning
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InconsistentVersionWarning)
            _if_model = joblib.load(str(ISOLATION_FOREST_PATH))
    except Exception as exc:
        _if_error = str(exc)
        _if_model = None
    return _if_model


def _parse_timestamp(value):
    """Parse the timestamp stored in air_quality (e.g. '2026-08-10 22:50:04')."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).strip())
    except ValueError:
        return None


def predict_aqi(reading):
    """Predict AQI for a reading dict using the trained Random Forest.

    The model was trained on ['pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2',
    'hour', 'day'] -> calculated_aqi (0–500).

    Returns {'aqi': int} or {'error': message}.
    """
    model = _load_random_forest()
    if model is None:
        return {'error': _rf_error or 'Model could not be loaded.'}

    dt = _parse_timestamp(reading.get('timestamp'))
    if dt is None:
        return {'error': 'Cannot parse reading timestamp to build hour/day features.'}

    feature_names = list(model.feature_names_in_)
    row = dict(reading)
    row['hour'] = dt.hour
    row['day'] = dt.day

    try:
        sample = [float(row[name]) for name in feature_names]
    except (KeyError, TypeError, ValueError) as exc:
        missing = [name for name in feature_names if name not in row]
        if missing:
            return {'error': f'Model expects features not available in the data: {missing}'}
        return {'error': f'Invalid feature value: {exc}'}

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        prediction = model.predict(np.array([sample]))[0]

    # Clamp to valid AQI range
    aqi_val = max(0, min(500, int(round(prediction))))
    return {'aqi': aqi_val, 'raw': float(prediction)}


def predict_anomaly(reading):
    """Run Isolation Forest anomaly detection on a reading dict.

    The model was trained on ['calculated_aqi', 'pm2_5', 'pm10', 'co', 'no2',
    'o3', 'so2'] (all available directly from the latest record). Returns
    {'is_anomaly': False} for a model output of 1 (Normal) and
    {'is_anomaly': True} for -1 (Anomaly), or {'error': message}.
    """
    model = _load_isolation_forest()
    if model is None:
        return {'error': _if_error or 'Model could not be loaded.'}

    feature_names = list(model.feature_names_in_)

    # Build the reading dict with the right key names for the model
    row = dict(reading)
    # The new model uses 'calculated_aqi'; map from 'calculated_aqi' in DB
    if 'calculated_aqi' in feature_names and 'calculated_aqi' not in row:
        row['calculated_aqi'] = row.get('aqi')

    try:
        sample = [float(row[name]) for name in feature_names]
    except (KeyError, TypeError, ValueError) as exc:
        missing = [name for name in feature_names if name not in row]
        if missing:
            return {'error': f'Model expects features not available in the data: {missing}'}
        return {'error': f'Invalid feature value: {exc}'}

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        prediction = model.predict(np.array([sample]))[0]

    return {'is_anomaly': int(prediction) == -1, 'raw': int(prediction)}


def annotate_anomalies(readings):
    """Return readings annotated with their anomaly-detection result.

    Reusable across views that need a per-reading anomaly status. Each input
    dict is copied and extended with 'is_anomaly' (bool or None) and
    'anomaly_error' (str or None).
    """
    annotated = []
    for reading in readings:
        item = dict(reading)
        result = predict_anomaly(reading)
        item['is_anomaly'] = result.get('is_anomaly')
        item['anomaly_error'] = result.get('error')
        annotated.append(item)
    return annotated


def _get_db_path():
    return str(Path(settings.BASE_DIR) / 'database' / 'air_quality.db')


def _mark_notified(ids):
    """Set notified=1 for the given row IDs."""
    if not ids:
        return
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(ids))
    cursor.execute(
        f"UPDATE air_quality SET notified = 1 WHERE id IN ({placeholders})",
        ids,
    )
    conn.commit()
    conn.close()


def send_anomaly_alert(readings):
    """Send an email for new anomalous readings not yet notified.

    Returns True if an email was sent, False otherwise.
    """
    new_anomalies = [
        r for r in readings
        if r.get('is_anomaly') is True and not r.get('notified')
    ]
    if not new_anomalies:
        return False

    from django.core.mail import send_mail

    lines = []
    for r in new_anomalies:
        lines.append(
            f"  {r.get('timestamp')}  |  AQI: {r.get('calculated_aqi')}  |  "
            f"PM2.5: {r.get('pm2_5')}  |  PM10: {r.get('pm10')}"
        )
    body = (
        f"Anomalous air quality readings detected in Kathmandu:\n\n"
        f"{'Timestamp':<22} {'AQI':>6}  {'PM2.5':>7}  {'PM10':>7}\n"
        + "\n".join(lines)
    )

    try:
        send_mail(
            subject=f"AQI Alert: {len(new_anomalies)} anomalous reading(s) detected",
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_RECIPIENT],
            fail_silently=True,
        )
    except Exception:
        return False

    _mark_notified([r['id'] for r in new_anomalies if r.get('id')])
    return True

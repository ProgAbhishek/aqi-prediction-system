import json
from datetime import datetime

from django.conf import settings
from django.shortcuts import render

from . import ml_services, services


def _latest_snapshot():
    """Return (latest, prediction, anomaly) for the latest DB record.

    Shared by views that show current/predicted/anomaly status so the
    DB + ML logic is not duplicated between them.
    """
    latest = services.get_latest_reading()
    if not latest:
        return None, None, None
    return latest, ml_services.predict_aqi(latest), ml_services.predict_anomaly(latest)


def index(request):
    """Dashboard - current AQI overview with prediction and anomaly status."""
    latest, prediction, anomaly = _latest_snapshot()

    # Build predicted AQI info and comparison
    predicted_aqi_info = None
    comparison = None
    if prediction and prediction.get('aqi') is not None:
        predicted_aqi_info = services.get_aqi_info(prediction['aqi'])
        comparison = services.compare_aqi(
            latest.get('calculated_aqi') if latest else None,
            prediction['aqi'],
        )

    # Build pollutant list for the dashboard
    pollutants = services.get_pollutants(latest) if latest else []

    # Historical data for the inline AQI trend chart (all records for filtering)
    historical_data = services.get_historical_data_all()

    context = {
        'latest': latest,
        'prediction': prediction,
        'predicted_aqi_info': predicted_aqi_info,
        'comparison': comparison,
        'anomaly': anomaly,
        'pollutants': pollutants,
        'total_records': services.count_records(),
        'historical_json': json.dumps(historical_data),
    }
    return render(request, 'dashboard/index.html', context)


def prediction(request):
    """Prediction - forecast AQI for a user-chosen date/time."""
    latest = services.get_latest_reading()

    predicted_aqi_info = None
    custom_prediction = None
    custom_aqi_info = None
    error_msg = None
    selected_dt = None

    if request.method == 'POST':
        dt_str = request.POST.get('target_datetime', '')
        if not dt_str:
            error_msg = 'Please select a date and time.'
        elif latest is None:
            error_msg = 'No sensor data available to base prediction on.'
        else:
            try:
                selected_dt = datetime.fromisoformat(dt_str)
            except ValueError:
                error_msg = 'Invalid date/time format.'
            else:
                custom_prediction = ml_services.predict_aqi_for_datetime(latest, selected_dt)
                if custom_prediction.get('error'):
                    error_msg = custom_prediction['error']
                else:
                    custom_aqi_info = services.get_aqi_info(custom_prediction['aqi'])

    # Default next-hour prediction for the hero card
    default_prediction = None
    default_aqi_info = None
    if latest:
        default_prediction = ml_services.predict_aqi(latest)
        if default_prediction.get('aqi') is not None:
            default_aqi_info = services.get_aqi_info(default_prediction['aqi'])

    pollutants = services.get_pollutants(latest) if latest else []

    context = {
        'latest': latest,
        'default_prediction': default_prediction,
        'default_aqi_info': default_aqi_info,
        'custom_prediction': custom_prediction,
        'custom_aqi_info': custom_aqi_info,
        'selected_dt': selected_dt.strftime('%Y-%m-%dT%H:%M') if selected_dt else '',
        'error_msg': error_msg,
        'pollutants': pollutants,
        'total_records': services.count_records(),
    }
    return render(request, 'dashboard/prediction.html', context)


def historical(request):
    """Historical Data - AQI and PM2.5 trend charts plus recent readings."""
    context = {
        'total_records': services.count_records(),
        'recent': services.get_recent_readings(20),
        'historical_json': json.dumps(services.get_historical_data_all()),
    }
    return render(request, 'dashboard/historical.html', context)


def anomaly(request):
    """Anomaly Detection - latest status plus per-reading anomaly results."""
    latest, _, anomaly_status = _latest_snapshot()

    recent = ml_services.annotate_anomalies(services.get_recent_readings(20))
    email_sent = ml_services.send_anomaly_alert(recent)

    context = {
        'latest': latest,
        'anomaly': anomaly_status,
        'total_records': services.count_records(),
        'recent': recent,
        'email_sent': email_sent,
        'EMAIL_RECIPIENT': settings.EMAIL_RECIPIENT,
    }
    return render(request, 'dashboard/anomaly.html', context)


def about(request):
    """About Project - static project information."""
    return render(request, 'dashboard/about.html')

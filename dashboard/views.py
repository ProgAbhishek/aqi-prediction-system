import json

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
    """Dashboard — current AQI overview with prediction and anomaly status."""
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

    # Historical data for the inline AQI trend chart
    historical_data = services.get_historical_data(50)

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
    """Prediction — current vs predicted AQI using the Random Forest model."""
    latest, prediction, _ = _latest_snapshot()

    predicted_aqi_info = None
    comparison = None
    if prediction and prediction.get('aqi') is not None:
        predicted_aqi_info = services.get_aqi_info(prediction['aqi'])
        comparison = services.compare_aqi(
            latest.get('calculated_aqi') if latest else None,
            prediction['aqi'],
        )

    pollutants = services.get_pollutants(latest) if latest else []

    context = {
        'latest': latest,
        'prediction': prediction,
        'predicted_aqi_info': predicted_aqi_info,
        'comparison': comparison,
        'pollutants': pollutants,
        'total_records': services.count_records(),
    }
    return render(request, 'dashboard/prediction.html', context)


def historical(request):
    """Historical Data — AQI and PM2.5 trend charts plus recent readings."""
    context = {
        'total_records': services.count_records(),
        'recent': services.get_recent_readings(20),
        'historical_json': json.dumps(services.get_historical_data()),
    }
    return render(request, 'dashboard/historical.html', context)


def anomaly(request):
    """Anomaly Detection — latest status plus per-reading anomaly results."""
    latest, _, anomaly_status = _latest_snapshot()

    context = {
        'latest': latest,
        'anomaly': anomaly_status,
        'total_records': services.count_records(),
        'recent': ml_services.annotate_anomalies(services.get_recent_readings(20)),
    }
    return render(request, 'dashboard/anomaly.html', context)


def about(request):
    """About Project — static project information."""
    return render(request, 'dashboard/about.html')

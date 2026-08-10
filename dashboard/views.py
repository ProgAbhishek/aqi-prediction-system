from django.shortcuts import render

from . import services


def index(request):
    """Dashboard home — shows the latest air quality reading from the existing DB."""

    context = {
        'latest': services.get_latest_reading(),
        'total_records': services.count_records(),
        'recent': services.get_recent_readings(10),
    }

    return render(request, 'dashboard/index.html', context)

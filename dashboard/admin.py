from django.contrib import admin
from .models import AirQuality, MLModel, AQIPrediction

admin.site.register(AirQuality)
admin.site.register(MLModel)
admin.site.register(AQIPrediction)

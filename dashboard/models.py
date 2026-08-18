from django.db import models

class AirQuality(models.Model):
    timestamp = models.DateTimeField(unique=True)
    pm2_5 = models.FloatField()
    pm10 = models.FloatField()
    co = models.FloatField()
    no2 = models.FloatField()
    o3 = models.FloatField()
    so2 = models.FloatField()
    aqi = models.IntegerField()

    def __str__(self):
        return f"AQI {self.aqi} at {self.timestamp}"

class MLModel(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    model_path = models.FilePathField(allow_folders=False)
    trained_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (v{self.version})"

class AQIPrediction(models.Model):
    timestamp = models.DateTimeField(unique=True)
    aqi_24h = models.IntegerField()
    aqi_48h = models.IntegerField()
    aqi_72h = models.IntegerField()
    aqi_96h = models.IntegerField()
    aqi_120h = models.IntegerField()
    pm2_5_pred = models.FloatField()
    pm10_pred = models.FloatField()
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"AQI Predictions at {self.timestamp} (24h: {self.aqi_24h})"

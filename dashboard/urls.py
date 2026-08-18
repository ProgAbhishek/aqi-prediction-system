from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('prediction/', views.prediction, name='prediction'),
    path('historical/', views.historical, name='historical'),
    path('anomaly/', views.anomaly, name='anomaly'),
    path('about/', views.about, name='about'),
]

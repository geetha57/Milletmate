from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Farmer Tool
    path('predict-price/', views.price_predictor, name='price_predictor'),
    
    # Admin Tools
    path('dashboard/', views.admin_analytics, name='admin_analytics'),
    path('upload-data/', views.upload_dataset, name='upload_dataset'),
]
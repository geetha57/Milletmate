from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Farmer AI Tools
    path('predict-price/', views.price_predictor, name='price_predictor'),
    path('demand-forecast/', views.demand_forecast, name='demand_forecast'), # Added
    
    # Buyer Insights
    path('market-trends/', views.demand_forecast, name='market_insights'), # Added (Reuse forecast logic)
    
    # Admin Tools
    path('admin-dashboard/', views.admin_analytics, name='admin_analytics'),
    path('upload-data/', views.upload_dataset, name='upload_dataset'),
]
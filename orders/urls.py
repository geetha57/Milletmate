from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Buyer URLs
    path('initialize/<int:product_id>/', views.place_order, name='place_order'),
    path('my-procurement/', views.buyer_history, name='buyer_history'),

    # Farmer URLs
    path('requests/', views.incoming_requests, name='incoming_requests'),
    path('update-status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
]
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Farmer URLs
    path('my-listings/', views.my_listings, name='my_listings'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),

    # Buyer URLs
    path('marketplace/', views.marketplace, name='marketplace'),
    path('detail/<int:pk>/', views.product_detail, name='product_detail'),
]
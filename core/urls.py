from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import landing_view

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Public Landing Page
    path('', landing_view, name='landing'),
    
    # App-Specific Routes
    path('accounts/', include('accounts.urls')),
    # path('products/', include('products.urls')),
    # path('orders/', include('orders.urls')),
    # path('analytics/', include('analytics.urls')),
    # path('notifications/', include('notifications.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Serving Media and Static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import landing_view, dashboard_view # Import both now

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Routes
    path('', landing_view, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'), # The Command Center URL
    
    # App-Specific Routes
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
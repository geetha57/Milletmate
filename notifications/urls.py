from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('inbox/', views.notification_inbox, name='inbox'),
    path('mark-read/<int:pk>/', views.mark_as_read, name='mark_as_read'),
    path('clear-all/', views.clear_all, name='clear_all'),
]
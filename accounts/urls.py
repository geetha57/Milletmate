from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- Authentication Protocol ---
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    
    # --- Role-Based Command Centers (Dashboards) ---
    # These act as the primary entry nodes for each stakeholder
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/farmer/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/buyer/', views.user_dashboard, name='buyer_dashboard'), # Added for Buyer node
    
    # --- Password Recovery Protocol ---
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]
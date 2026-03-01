from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
import random

from .models import EmailOTP
from products.models import MilletProduct
from orders.models import Order
from analytics.models import SalesHistory

User = get_user_model()

# --- AUTHENTICATION PROTOCOLS ---

def login_view(request):
    """Protocol for stakeholder authentication and role-based routing"""
    if request.user.is_authenticated:
        return redirect('landing') # Landing view handles smart redirection

    if request.method == 'POST':
        email = request.POST.get('username')  
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user:
            if not user.is_active:
                messages.error(request, _('Security Protocol: Please verify your email node first.'))
                return render(request, 'accounts/login.html')
            
            login(request, user)
            user.login_count += 1
            user.save()
            
            # Role-Based Automated Redirection
            if user.role == 'admin':
                messages.success(request, _('Admin Node Access Authorized.'))
                return redirect('analytics:admin_analytics')
            elif user.role == 'farmer':
                messages.success(request, _('Farmer Dashboard Initialized.'))
                return redirect('products:my_listings')
            else: # Buyer
                messages.success(request, _('Marketplace Procurement Node Active.'))
                return redirect('products:marketplace')
        
        messages.error(request, _('Invalid Credentials. Access Denied.'))
    return render(request, 'accounts/login.html')

def signup_view(request):
    """Initializes a new stakeholder node in the value chain"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'farmer') # Default to farmer if not specified
        
        if User.objects.filter(email=email).exists():
            messages.info(request, _('Account Node already exists. Please login.'))
            return redirect('accounts:login')
        
        # Create inactive user until OTP is verified
        user = User.objects.create_user(email=email, password=password, role=role, is_active=False)
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})
        
        try:
            send_mail(
                _('Verify your MilletChain Account'),
                _('Your Security OTP code is: {}. It expires in 10 minutes.').format(otp),
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['verify_user'] = user.id
            return redirect('accounts:verify_otp')
        except Exception as e:
            # Cleanup user if mail fails during development
            user.delete()
            messages.error(request, _('SMTP Transmission Error. Check configuration.'))
            
    return render(request, 'accounts/signup.html')

def verify_otp_view(request):
    """Validates the security token for account activation"""
    user_id = request.session.get('verify_user')
    if not user_id:
        return redirect('accounts:signup')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()
        
        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.is_verified = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')
            
        messages.error(request, _('Invalid or Expired Security Token.'))
    return render(request, 'accounts/verify_otp.html')

# --- DYNAMIC DASHBOARDS (Redirect placeholders) ---

@login_required
def logout_view(request):
    """Terminates active session and disconnects node"""
    logout(request)
    messages.info(request, _('Node Disconnected. Session Safely Terminated.'))
    return redirect('landing')

# Note: Individual app dashboards are handled within 'products', 'analytics', and 'orders' apps 
# for better modularity. The views below are secondary fallbacks.

@login_required
def user_dashboard(request):
    """Redirects user to their role-specific dashboard if they land here"""
    if request.user.role == 'farmer':
        return redirect('products:my_listings')
    elif request.user.role == 'buyer':
        return redirect('products:marketplace')
    return redirect('analytics:admin_analytics')
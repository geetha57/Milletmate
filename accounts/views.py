from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
import random

# Future App Imports (Update these as we build other apps)
# from ml.models import CropRecommendation, YieldPrediction
# from chatbot.models import ChatLog

User = get_user_model()
from .models import EmailOTP

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Please verify your email first.')
                return render(request, 'accounts/login.html')
            login(request, user)
            user.login_count += 1
            user.save()
            return redirect('accounts:admin_dashboard' if user.role == 'admin' else 'accounts:user_dashboard')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'farmer')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Account already exists. Please login.')
            return redirect('accounts:login')
        
        user = User.objects.create_user(email=email, password=password, role=role, is_active=False)
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})
        
        try:
            send_mail(
                'Verify your Agri-Tech Account',
                f'Your OTP verification code is: {otp}. It expires in 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['verify_user'] = user.id
            return redirect('accounts:verify_otp')
        except:
            messages.error(request, 'SMTP Error. Check your .env settings.')
    return render(request, 'accounts/signup.html')

def verify_otp_view(request):
    user_id = request.session.get('verify_user')
    if not user_id: return redirect('accounts:signup')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()
        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active, user.is_verified = True, True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')
        messages.error(request, 'Invalid/Expired OTP.')
    return render(request, 'accounts/verify_otp.html')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin': return redirect('accounts:user_dashboard')
    
    # Placeholder metrics for AI monitoring (update once ML app is ready)
    context = {
        'total_farmers': User.objects.filter(role='farmer').count(),
        'total_recommendations': 0, # Update after ML App
        'total_yield_queries': 0,    # Update after ML App
        'recent_users': User.objects.all().order_by('-date_joined')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('landing')
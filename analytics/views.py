import csv
import io
import os
import joblib
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg, Sum
from .models import SalesHistory, MLModelMetric
from products.models import MilletProduct
from accounts.models import User

# ==========================================
# 🤖 ML MODEL INITIALIZATION
# ==========================================
MODEL_PATH = os.path.join(settings.BASE_DIR, 'analytics', 'ml_models', 'millet_price_model.pkl')

try:
    trained_pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    trained_pipeline = None
    print(f"⚠️ ML Model Alert: {e}. Simulation mode active.")

# ==========================================
# 👨‍🌾 FARMER: PRICE PREDICTION (REAL AI)
# ==========================================
@login_required
def price_predictor(request):
    global trained_pipeline # Fixed UnboundLocalError
    
    suggested_price = None
    prediction_type = "AI Engine"

    if request.method == 'POST':
        millet_type = request.POST.get('millet_type')
        location = request.POST.get('location')
        quantity = request.POST.get('quantity_kg', 500)
        season = request.POST.get('season', 'Kharif')

        if trained_pipeline:
            try:
                input_df = pd.DataFrame([{
                    "millet_type": millet_type.capitalize(),
                    "quantity_kg": float(quantity),
                    "location": location.capitalize(),
                    "season": season.capitalize()
                }])
                
                prediction = trained_pipeline.predict(input_df)[0]
                suggested_price = round(float(prediction), 2)
            except Exception as e:
                print(f"Prediction Error: {e}")
                # Don't set global to None here to avoid affecting other users, 
                # just fall back locally.
        
        if suggested_price is None:
            prediction_type = "Historical Average"
            avg_price = SalesHistory.objects.filter(
                millet_type=millet_type, 
                location__icontains=location
            ).aggregate(Avg('price'))['price__avg']
            
            suggested_price = round(float(avg_price), 2) if avg_price else 45.00

    return render(request, 'analytics/price_predictor.html', {
        'suggested_price': suggested_price,
        'prediction_type': prediction_type,
        'millet_types': SalesHistory.MILLET_TYPES
    })

# ==========================================
# 📈 DEMAND FORECASTING
# ==========================================
@login_required
def demand_forecast(request):
    trends = SalesHistory.objects.values('month').annotate(
        total_qty=Sum('quantity_sold')
    ).order_by('month')

    months = [t['month'] for t in trends]
    quantities = [float(t['total_qty']) for t in trends]
    forecast_val = sum(quantities[-3:]) / 3 if len(quantities) >= 3 else 0

    return render(request, 'analytics/demand_forecast.html', {
        'months': months,
        'quantities': quantities,
        'forecast_val': round(forecast_val, 2)
    })

# ==========================================
# 🛠️ ADMIN: ANALYTICS DASHBOARD
# ==========================================
@login_required
def admin_analytics(request):
    if request.user.role != 'admin':
        return redirect('landing')

    # Core Stats
    total_orders = SalesHistory.objects.count()
    avg_market_price = SalesHistory.objects.aggregate(Avg('price'))['price__avg']
    top_millet = SalesHistory.objects.values('millet_type').annotate(
        total_sales=Sum('quantity_sold')
    ).order_by('-total_sales').first()

    # ML Intelligence
    metrics = MLModelMetric.objects.all()

    # Dynamic Node Activity Feed (Real-time logs)
    # Get 3 most recent users and 2 most recent crop listings
    recent_users = User.objects.all().order_by('-id')[:3]
    recent_crops = MilletProduct.objects.all().order_by('-created_at')[:2]

    return render(request, 'analytics/admin_dashboard.html', {
        'total_orders': total_orders,
        'avg_market_price': avg_market_price,
        'top_millet': top_millet,
        'metrics': metrics,
        'recent_users': recent_users,
        'recent_crops': recent_crops
    })

@login_required
def upload_dataset(request):
    if request.user.role != 'admin':
        return redirect('landing')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        next(io_string) 
        
        history_nodes = []
        for row in csv.reader(io_string, delimiter=','):
            history_nodes.append(SalesHistory(
                millet_type=row[0].lower(),
                month=int(row[1]),
                location=row[2],
                quantity_sold=row[3],
                price=row[4]
            ))
        
        SalesHistory.objects.bulk_create(history_nodes)
        messages.success(request, "Dataset integrated into ML training node successfully.")
        return redirect('analytics:admin_analytics')

    return render(request, 'analytics/upload_dataset.html')
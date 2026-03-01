import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalesHistory, MLModelMetric
from products.models import MilletProduct
from django.db.models import Avg, Sum

# --- FARMER: PRICE PREDICTION ---
@login_required
def price_predictor(request):
    suggested_price = None
    if request.method == 'POST':
        millet_type = request.POST.get('millet_type')
        location = request.POST.get('location')
        
        # Simple Regression Simulation: Average price for this millet in this location
        avg_price = SalesHistory.objects.filter(
            millet_type=millet_type, 
            location__icontains=location
        ).aggregate(Avg('price'))['price__avg']
        
        if avg_price:
            suggested_price = round(float(avg_price), 2)
        else:
            # Fallback if no history exists
            suggested_price = 45.00 
            
    return render(request, 'analytics/price_predictor.html', {
        'suggested_price': suggested_price,
        'millet_types': SalesHistory.MILLET_TYPES
    })

# --- ADMIN: ANALYTICS DASHBOARD ---
@login_required
def admin_analytics(request):
    if request.user.role != 'admin':
        return redirect('landing')

    total_orders = SalesHistory.objects.count()
    avg_market_price = SalesHistory.objects.aggregate(Avg('price'))['price__avg']
    top_millet = SalesHistory.objects.values('millet_type').annotate(
        total_sales=Sum('quantity_sold')
    ).order_by('-total_sales').first()

    metrics = MLModelMetric.objects.all()

    return render(request, 'analytics/admin_dashboard.html', {
        'total_orders': total_orders,
        'avg_market_price': avg_market_price,
        'top_millet': top_millet,
        'metrics': metrics
    })

# --- ADMIN: CSV DATASET UPLOADER ---
@login_required
def upload_dataset(request):
    if request.user.role != 'admin':
        return redirect('landing')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        next(io_string) # Skip header
        
        for row in csv.reader(io_string, delimiter=','):
            SalesHistory.objects.create(
                millet_type=row[0],
                month=row[1],
                location=row[2],
                quantity_sold=row[3],
                price=row[4]
            )
        messages.success(request, "Dataset integrated into ML training node.")
        return redirect('analytics:admin_analytics')

    return render(request, 'analytics/upload_dataset.html')
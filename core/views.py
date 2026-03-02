from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from products.models import MilletProduct
from orders.models import Order
from analytics.models import SalesHistory, MLModelMetric

# --- PUBLIC LANDING PAGE ---
def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {
        'total_listings': MilletProduct.objects.count(),
        'active_nodes': SalesHistory.objects.count(),
    }
    return render(request, 'landing.html', context)

# --- STAKEHOLDER DASHBOARD (The Command Center) ---
@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    # --- FARMER DASHBOARD DATA ---
    if user.role == 'farmer':
        my_products = MilletProduct.objects.filter(farmer=user)
        context['total_earnings'] = Order.objects.filter(product__farmer=user, status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['active_listings'] = my_products.count()
        context['pending_orders'] = Order.objects.filter(product__farmer=user, status='pending').count()
        
        # Stock Chart Data
        context['chart_labels'] = [p.get_millet_type_display() for p in my_products[:5]]
        context['chart_values'] = [float(p.quantity) for p in my_products[:5]]
        context['chart_type'] = 'bar'

    # --- BUYER DASHBOARD DATA ---
    elif user.role == 'buyer':
        my_orders = Order.objects.filter(buyer=user)
        context['total_spent'] = my_orders.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['active_procurements'] = my_orders.exclude(status__in=['completed', 'rejected']).count()
        context['trending_millet'] = SalesHistory.objects.values('millet_type').annotate(total=Sum('quantity_sold')).order_by('-total').first()
        
        # Price Trends Chart Data
        history = SalesHistory.objects.order_by('month')[:6]
        context['chart_labels'] = [f"Month {h.month}" for h in history]
        context['chart_values'] = [float(h.price) for h in history]
        context['chart_type'] = 'line'

    # --- ADMIN DASHBOARD DATA ---
    elif user.role == 'admin':
        from accounts.models import User as AccountUser
        context['total_users'] = AccountUser.objects.count()
        context['total_platform_sales'] = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['ml_metrics'] = MLModelMetric.objects.all()

        # Admin Global Chart Data (Average price across all millets)
        global_history = SalesHistory.objects.values('month').annotate(avg_price=Avg('price')).order_by('month')
        context['chart_labels'] = [f"Month {h['month']}" for h in global_history]
        context['chart_values'] = [float(h['avg_price']) for h in global_history]
        context['chart_type'] = 'line'

    return render(request, 'core/dashboard.html', context)
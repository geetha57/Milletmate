from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from products.models import MilletProduct
from orders.models import Order
from analytics.models import SalesHistory, MLModelMetric

@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    # --- FARMER DASHBOARD DATA ---
    if user.role == 'farmer':
        my_products = MilletProduct.objects.filter(farmer=user)
        context['active_listings'] = my_products.count()
        context['pending_orders'] = Order.objects.filter(product__farmer=user, status='pending').count()
        context['total_earnings'] = Order.objects.filter(product__farmer=user, status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Data for Stock Chart
        context['stock_labels'] = [p.get_millet_type_display() for p in my_products[:5]]
        context['stock_values'] = [float(p.quantity) for p in my_products[:5]]

    # --- BUYER DASHBOARD DATA ---
    elif user.role == 'buyer':
        my_orders = Order.objects.filter(buyer=user)
        context['total_spent'] = my_orders.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['active_procurements'] = my_orders.exclude(status__in=['completed', 'rejected']).count()
        
        # Market Insights (Sales History)
        context['trending_millet'] = SalesHistory.objects.values('millet_type').annotate(total=Sum('quantity_sold')).order_by('-total').first()
        
        # Price Trends for Chart
        history = SalesHistory.objects.order_by('month')[:6]
        context['price_labels'] = [f"Month {h.month}" for h in history]
        context['price_values'] = [float(h.price) for h in history]

    # --- ADMIN DASHBOARD DATA ---
    elif user.role == 'admin':
        context['total_users'] = user.__class__.objects.count()
        context['total_platform_sales'] = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['ml_metrics'] = MLModelMetric.objects.all()

    return render(request, 'core/dashboard.html', context)
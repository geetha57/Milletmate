from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

from .models import Order
from products.models import MilletProduct
from notifications.models import Notification

# --- BUYER ACTIONS ---

@login_required
def place_order(request, product_id):
    """Protocol for Buyer to initialize a purchase request"""
    product = get_object_or_404(MilletProduct, pk=product_id)

    if request.method == 'POST':
        order_qty = Decimal(request.POST.get('quantity'))

        if order_qty <= 0 or order_qty > product.quantity:
            messages.error(request, "Invalid quantity. Check available stock.")
            return redirect('products:product_detail', pk=product_id)

        total_cost = order_qty * product.price

        order = Order.objects.create(
            buyer=request.user,
            product=product,
            quantity=order_qty,
            total_price=total_cost,
            status='pending'
        )

        # TRIGGER: Farmer Notification
        Notification.objects.create(
            recipient=product.farmer,
            notification_type='order',
            title="New Acquisition Request",
            message=f"A buyer has requested {order_qty}kg of your {product.get_millet_type_display()}.",
            link='/orders/requests/'
        )

        messages.success(request, "Acquisition request transmitted to the Farmer.")
        return redirect('orders:buyer_history')

    return redirect('products:product_detail', pk=product_id)

@login_required
def buyer_history(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'orders/buyer_history.html', {'orders': orders})

# --- FARMER ACTIONS ---

@login_required
def incoming_requests(request):
    orders = Order.objects.filter(product__farmer=request.user)
    return render(request, 'orders/incoming_requests.html', {'orders': orders})

@login_required
def update_order_status(request, order_id, status):
    """Farmer protocol to Accept, Reject, or Complete an order"""
    order = get_object_or_404(Order, pk=order_id, product__farmer=request.user)

    if status in ['accepted', 'rejected', 'completed']:
        order.status = status
        order.save()

        # TRIGGER: Buyer Notification (The Missing Piece)
        Notification.objects.create(
            recipient=order.buyer,
            notification_type='order',
            title=f"Order Update: {status.upper()}",
            message=f"Your request for {order.product.get_millet_type_display()} has been {status}.",
            link='/orders/my-procurement/'
        )

        if status == 'accepted':
            product = order.product
            product.quantity -= order.quantity
            if product.quantity <= 0:
                product.is_available = False
            product.save()

        messages.success(request, f"Order #{order.id} status updated to {status.upper()}.")

    return redirect('orders:incoming_requests')
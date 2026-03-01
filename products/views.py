from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MilletProduct
from .forms import ProductForm
from django.db.models import Q

# --- FARMER VIEWS ---

@login_required
def my_listings(request):
    """View for Farmers to see and manage their own products"""
    products = MilletProduct.objects.filter(farmer=request.user)
    return render(request, 'products/my_listings.html', {'products': products})

@login_required
def add_product(request):
    """View for Farmers to add a new millet listing"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            messages.success(request, "Millet product listed successfully in the value chain.")
            return redirect('products:my_listings')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def edit_product(request, pk):
    """View for Farmers to update existing listings"""
    product = get_object_or_404(MilletProduct, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product metadata updated successfully.")
            return redirect('products:my_listings')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def delete_product(request, pk):
    """Delete a listing from the value chain"""
    product = get_object_or_404(MilletProduct, pk=pk, farmer=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product removed from the ecosystem.")
        return redirect('products:my_listings')
    return render(request, 'products/confirm_delete.html', {'product': product})


# --- BUYER VIEWS ---

def marketplace(request):
    """Public/Buyer view to browse and search products"""
    query = request.GET.get('q')
    millet_filter = request.GET.get('millet_type')
    location_filter = request.GET.get('location')

    products = MilletProduct.objects.filter(is_available=True)

    if query:
        products = products.filter(Q(description__icontains=query) | Q(location__icontains=query))
    if millet_filter:
        products = products.filter(millet_type=millet_filter)
    if location_filter:
        products = products.filter(location__icontains=location_filter)

    millet_types = MilletProduct.MILLET_TYPES
    return render(request, 'products/marketplace.html', {
        'products': products,
        'millet_types': millet_types
    })

def product_detail(request, pk):
    """Detailed view for buyers to see farmer info before ordering"""
    product = get_object_or_404(MilletProduct, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})
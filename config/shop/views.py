from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from .cart import Cart
from django.views.decorators.http import require_POST


# Create your views here.

def product_list(request, category_slug=None):
    category=None
    categories=Category.objects.all()
    products=Product.objects.filter(is_active=True)
    if category_slug:
        category=get_object_or_404(Category, slug=category_slug)
        products=products.filter(category=category)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product=get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/product/detail.html', {'product':product})

def cart_detail(request):
    cart=Cart(request)
    return render(request, 'shop/cart/detail.html')

@require_POST
def cart_add(request, product_id):
    cart=Cart(request)
    product=get_object_or_404(Product, id=product_id, is_active=True)
    qty = max(1, int(request.POST.get('quantity', 1)))
    cart.add(product, quantity=qty)
    return redirect('shop:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart=Cart(request)
    product=get_object_or_404(Product, id=product_id, is_active=True)
    qty=max(0, int(request.POST.get('quantity',1)))
    cart.add(product,quantity=qty, update_quantity=True) #0-deletes
    return redirect('shop:cart_detail')
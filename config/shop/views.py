from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .forms import ProductForm, OrderCreateForm
from django.contrib import messages

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
    return render(request, 'shop/cart/detail.html', {'cart': cart})

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

@login_required
@permission_required('shop.change_product', raise_exception=True)
def manage_products(request):
    products=Product.objects.all().order_by('-id')
    return render(request, 'shop/manage/products_list.html', {'products': products})

@login_required
@permission_required('shop.add_product', raise_exception=True)
def product_create(request):
    if request.method=='POST':
        form=ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product=form.save()
            messages.success(request, f'Product "{product.name}" created')
            return redirect('shop:manage_products')
    else:
        form=ProductForm()
    return render(request, 'shop/manage/product_form.html', {'form':form, 'mode':'create'})

@login_required
@permission_required('shop.change_product', raise_exception=True)
def product_edit(request, pk):
    product=get_object_or_404(Product, pk=pk)
    if request.method=='POST':
        form=ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated')
            return redirect('shop:manage_products')
    else:
        form=ProductForm(instance=product)
    return render(request, 'shop/manage/product_form.html', {'form':form, 'mode':'edit', 'product':product})

def checkout(request):
    cart=Cart(request)
    if len(cart)==0:
        return redirect('shop:cart_detail')
    if request.method=='POST':
        form=OrderCreateForm(request.POST)
        if form.is_valid():
            order=form.save(commit=False)
            order.paid=False
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            total=order.get_total_cost()
            cart.clear()
            return render(request, 'shop/order/receipt.html',{
                'order':order,
                'total':total,
            })
    else:
        form=OrderCreateForm
        return render(request, 'shop/order/checkout.html',{
            'cart':cart,
            'form':form
        })
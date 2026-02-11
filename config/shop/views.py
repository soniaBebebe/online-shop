from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .forms import ProductForm, OrderCreateForm
from django.contrib import messages
from .email import send_order_confirmation, send_order_receipt, notify_admin, send_order_pdf
from .pdf import generate_order_pdf
from django.http import FileResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum, Count, F, DecimalField
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core.paginator import Paginator
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncDate

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
            if request.user.is_authenticated:
                order.user=request.user
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
            send_order_confirmation(order)
            send_order_receipt(order)
            notify_admin(order)
            send_order_pdf(order)
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

def order_pdf(request, order_id):
    order=Order.objects.get(id=order_id)
    pdf_buffer=generate_order_pdf(order)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"receipt_{order.id}.pdf")

@login_required
def my_orders(request):
    orders=Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/order/my_orders.html", {"orders": orders})

def signup(request):
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            return redirect("shop:home")
    else:
        form=UserCreationForm()
    return render(request, "shop/auth/signup.html", {"form": form})

# @login_required
# @permission_required('shop.view_order', raise_exception=True)
# def manage_dashboard(request):
#     from .models import Order
#     today=timezone.now().date()
#     week_ago=today-timedelta(days=7)
#     total_orders=Order.objects.count()
#     paid_orders=Order.objects.filter(paid=True).count()
#     week_orders=Order.objects.filter(created__date__gte=week_ago).count()

#     revenue=Order.objects.filter (paid=True).aggregate(s=Sum('total'))['s'] or 0
#     recent_orders=Order.objects.order_by('-created')[:10]

#     return render(request, 'shop/manage/dasboard.html',{
#         'total_orders':total_orders,
#         'paid_orders':paid_orders,
#         'week_orders':week_orders,
#         'revenue': revenue,
#         'recent_orders': recent_orders,
#     })

@login_required
@permission_required('shop.view_order', raise_exception=True)
def manage_orders(request):
    from .models import Order
    status=request.GET.get('status')
    qs=Order.objects.order_by('-created')
    q=(request.GET.get('q') or '').strip()
    paid=(request.GET.get('paid') or '').strip()
    if q:
        qs=qs.filter(
            Q(first_name__icontains=q)|
            Q(last_name__icontains=q)|
            Q(email__icontains=q)|
            Q(id__icontains=q)
        )
    if status:
        qs=qs.filter(status=status)
    if paid=='yes':
        qs=qs.filter(paid=True)
    elif paid=='no':
        qs=qs.filter(paid=False)
    paginator=Paginator(qs,20)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    context={
        'status':status,
        'page_obj':page_obj,
        'q':q,
        'paid':paid,
        'status_choices':Order.STATUS_CHOICES,
    }
    return render(request, 'shop/manage/orders_list.html', context)

@login_required
@permission_required('shop.view_order', raise_exception=True)
def manage_order_detail(request, order_id):
    from .models import Order
    order=get_object_or_404(Order, id=order_id)
    items=order.items.select_related('product')
    return render(request, 'shop/manage/order_detail.html',{
        'order':order,
        'items':items,
    })

@login_required
@permission_required('shop.change_order', raise_exception=True)
@require_POST
def manage_order_status(request, order_id):
    from .models import Order
    order=get_object_or_404(Order, id=order_id)

    new_status=request.POST.get('status')
    allowed={c[0] for c in Order.STATUS_CHOICES}
    if new_status in allowed:
        order.status=new_status
        order.save(update_fields=['status'])
        messages.success(request, f'Order #{order.id} status updated')
    
    return redirect('shop:manage_order_detail', order_id=order.id)

@login_required
@permission_required('shop.change_order', raise_exception=True)
@require_POST
def manage_orders_bulk_status(request):
    from .models import Order
    ids=request.POST.getlist('order_ids')
    new_status=(request.POST.get('status')or '').strip()
    allowed={c[0] for c in Order.STATUS_CHOICES}
    if not ids:
        messages.warning(request, "select at least one order")
        return redirect('shop:manage_orders')
    if new_status not in allowed:
        messages.error(request, "invalid status")
        return redirect('shop:manage_orders')
    updated=Order.objects.filter(id__in=ids).update(status=new_status)
    messages.success(request, f"Updated {updated} order(s)")
    return redirect('shop:manage_orders')

@login_required
@permission_required('shop.view_order', raise_exception=True)
def manage_dashboard(request):
    today=timezone.now().date()
    week_ago = today-timedelta(days=6)

    orders=(
        Order.objects
        .filter(created__date__gte=week_ago)
        .annotate(day=TruncDate("created"))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
        #nachat zdes
    )
    revenue=(
        Order.objects
        .filter(paid=True, created__date__gte=week_ago)
        .annotate(day=TruncDate("created"))
        .values('day')
        .annotate(
            total=Sum(
                F("items__price") * F("items__quantity"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by('day')
    )
    status_data=(
        Order.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by("status")
    )
    total_orders=Order.objects.count()
    paid_orders=Order.objects.filter(paid=True).count()
    week_orders=Order.objects.filter(created__date__gte=week_ago).count()
    revenue_total=revenue.aggregate(s=Sum("total"))["s"] or 0
    recent_orders=Order.objects.order_by("-created")[:10]
    context={
        "orders_data":list(orders),
        "revenue_data":list(revenue),
        "status_data":list(status_data),
    }
    return render(request, 'shop/manage/dashboard.html', context)
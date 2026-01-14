from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name='shop'
urlpatterns=[
    path('', views.product_list, name='home'),
    path('category/<slug:category_slug>/', views.product_list, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product'),
    path('cart/', views.cart_detail, name='cart_detail'),

    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/create/', views.product_create, name='product_create'),
    path('manage/products/<int:pk>/edit/', views.product_edit, name='product_edit'),

    path('checkout/', views.checkout, name='checkout'),

    path('order/<int:order_id>/pdf/', views.order_pdf, name='order_pdf'),
    path("my/orders/", views.my_orders, name="my_orders"),

    path("login/", auth_views.LoginView.as_view(template_name="shop/auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),

    path('manage/', views.manage_dashboard, name='manage_dashboard'),
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/create/', views.product_create, name='product_create'),
    path('manage/products/<int:pk>/edit/', views.product_edit, name='product_edit'),

    path('manage/orders', views.manage_orders, name='manage_orders'),
    path('manage/orders/<int:order_id>/', views.manage_order_detail, name='manage_order_detail'),
    path('manage/orders/<int:order_id>/status/', views.manage_order_status, name='manage_order_status'),

    path('manage/orders/bulk-status/', views.manage_orders_bulk_status, name="manage_orders_bulk_status"),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views

app_name='shop'
urlpatterns=[
    path('', views.product_list, name='home'),
    path('category/<slug:category_slug>/', views.product_list, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product'),
    path('cart/', views.cart_detail, name='cart_detail'),

    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
]
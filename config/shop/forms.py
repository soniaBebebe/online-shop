from django import forms
from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['category', 'name', 'slug', 'price', 'unit', 'stock', 'is_active', 'image', 'description']

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['first_name', 'last_name', 'email', 'address', 'city']
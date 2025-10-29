from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['category', 'name', 'slug', 'price', 'unit', 'stock', 'is_active', 'image', 'description']
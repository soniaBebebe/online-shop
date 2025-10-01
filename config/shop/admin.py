from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'slug')
    prepopulated_fields={'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('name', 'category', 'price', 'unit', 'is_weighted', 'is_active')
    list_filter=('category', 'is_active', 'is_weighted')
    search_fields=('name',)
    prepopulated_fields={'slug': ('name',)}
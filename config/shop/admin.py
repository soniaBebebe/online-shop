from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html

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

    def preview(self,obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.image.url)
        return "--"
    preview.short_description="Image"
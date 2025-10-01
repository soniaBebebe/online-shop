from django.db import models
from django.urls import reverse
from decimal import Decimal

class Category(models.Model):
    name=models.CharField(max_length=120)
    slug=models.SlugField(max_length=140, unique=True)

    class Meta:
        ordering=['name']
        verbose_name='Category'
        verbose_name_plural='Categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:category', args=[self.slug])

class Product(models.Model):
    category=models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name=models.CharField(max_length=180)
    slug=models.SlugField(max_length=200, unique=True)
    price=models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_weighted=models.BooleanField(default=False, help_text='Drobnoe kolichestvo (ex: kg)')
    stock=models.PositiveIntegerField(default=100)
    is_active=models.BooleanField(default=True)
    unit=models.CharField(max_length=20, default='pcs')

    class Meta:
        ordering=['name']
        indexes=[models.Index(fields=['slug']), models.Index(fields=['name'])]
        verbose_name='Product'
        verbose_name_plural='Products'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product', args=[self.slug])
    
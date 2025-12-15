from django.db import models
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

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
    image=models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)
    description=models.TextField(blank=True)

    class Meta:
        ordering=['name']
        indexes=[models.Index(fields=['slug']), models.Index(fields=['name'])]
        verbose_name='Product'
        verbose_name_plural='Products'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product', args=[self.slug])
    
class Order(models.Model):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50, blank=True)
    email=models.EmailField()
    address=models.CharField(max_length=50)
    city=models.CharField(max_length=100, blank=True)
    created=models.DateTimeField(default=timezone.now, db_index=True)
    paid=models.BooleanField(default=False)
    payment_id=models.CharField(max_length=100, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    class Meta:
        ordering=['-created']
    def __str__(self):
        return f"Order #{self.id}"
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product=models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    def get_cost(self):
        return self.price*self.quantity
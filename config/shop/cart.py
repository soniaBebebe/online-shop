from decimal import Decimal
from django.conf import settings
from .models import Product

CART_SESSION_ID = getattr(settings, "CART_SESSION_ID", "cart")

class Cart:
    def __init__(self, request):
        self.session=request.session
        cart=self.session.get(CART_SESSION_ID)
        if cart is None:
            cart=self.session[CART_SESSION_ID]={}
        self.cart=cart

    def add(self, product: Product, quantity: int=1, update_quantity:bool=False):
        pid=str(product.id)
        if pid not in self.cart:
            self.cart[pid]={"quantity":0, "price":str(product.price)}
        if update_quantity:
            self.cart[pid]["quantity"]=max(0, int(quantity))
        else:
            self.cart[pid]["quantity"]+=max(0, int(quantity))
        if self.cart[pid]["quantity"] <=0:
            del self.cart[pid]
        self.save()

    def remove(self, product:Product):
        pid=str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID]={}
        self.cart=self.session[CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified=True

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())
    
    def __iter__(self):
        product_ids=[int(pid) for pid in self.cart.keys()]
        if not product_ids:
            return
        products=Product.objects.filter(id__in=product_ids)
        cart=self.cart.copy()

        for product in products:
            item=cart[str(product.id)]
            item["product"]=product
            item["price"]=Decimal(item["price"])
            item["total_price"]=item["price"]* item["quantity"]
            yield item
    
    def get_total_price(self)->Decimal:
        return sum(Decimal(i["price"])*i["quantity"] for i in self.cart.values())
    
    def set(self, product: Product, quantity: int):
        pid = str(product.id)
        self.cart[pid]={"quantity": max(0, int(quantity)), "price": str(product.price)}
        if self.cart[pid]["quantity"]<=0:
            del self.cart[pid]
        self.save()

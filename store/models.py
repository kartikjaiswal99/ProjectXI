from django.db import models
from django.conf import settings
from uuid import uuid4
from django.utils.text import slugify
import uuid
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    size = models.CharField(max_length=12)

    def __str__(self):
        return self.size


class Product(models.Model):
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    sizes = models.ManyToManyField(
        'Size', related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    
class ProductImage(models.Model):
    product = models.ForeignKey('Product', models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images')


class Customer(models.Model):
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def first_name(self):
        return self.user.first_name
    
    def last_name(self):    
        return self.user.last_name
    

class Address(models.Model):
    user = models.ForeignKey(
        'Customer', related_name="addresses", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=False)

    country = models.CharField(max_length=100, blank=False)
    apartment_address = models.CharField(max_length=100, blank=False)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=False)
    postal_code = models.CharField(max_length=20, blank=False)
    state = models.CharField(max_length=100, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

 
class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    shipping_address = models.ForeignKey(
        'Address', related_name="shipping_orders", on_delete=models.SET_NULL, blank=True, null=True)

    @property
    def get_grand_total(self):
        items = self.items.all()
        total = sum([item.quantity * item.product.unit_price for item in items])
        return total
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="product_orders", on_delete=models.CASCADE
    )
    size = models.ForeignKey(
        Size, related_name="size_orders", on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        'Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE)
    size = models.ForeignKey(
        'Size', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'product','size']]
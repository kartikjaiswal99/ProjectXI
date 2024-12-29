from rest_framework import serializers
from .models import Order, OrderItem, Product, Category, ProductImage, Size, Cart, CartItem, Customer, Address
from django.db import transaction, models


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source = 'user.username', read_only=True)
    email = serializers.CharField(source = 'user.email', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'email', 'phone_number']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size']


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_slug = self.context['product_slug']
        product = Product.objects.get(slug=product_slug)
        return ProductImage.objects.create(product=product, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    sizes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Size.objects.all()
    ) 

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'slug', 'description', 'details', 'price', 'stock', 'sizes', 'images', 'created_at']
        read_only_fields = ['slug', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count', 'slug']
        read_only_fields = ['slug']

    products_count = serializers.IntegerField(read_only=True)


class CartItemProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'slug', 'name', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'size', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Product not found with given id')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']  
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        size = self.validated_data['size']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id, size=size)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity', 'size']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'size', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    def get_grand_total(self, obj):
        total = 0
        for item in obj.order_items.all():
            total += item.quantity * item.product.price
        return total

    class Meta:
        model = Order
        fields = ['id', 'customer', 'payment_status', 'shipping_address', 'placed_at', 'order_items', 'grand_total']
        # read_only_fields = ['total_price', 'payment_status']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'apartment_address', 'street_address', 'postal_code', 'city', 'state', 'country']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    full_name = serializers.CharField(max_length=255, required=True)
    apartment_address = serializers.CharField(max_length=100, required=True)
    street_address = serializers.CharField(max_length=100, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=20, required=True)
    city = serializers.CharField(max_length=100, required=True)
    state = serializers.CharField(max_length=100, required=True)
    country = serializers.CharField(max_length=100, required=True)


    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('Cart Not found with given id')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is empty')
        return cart_id


    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            (customer, created) = Customer.objects.get_or_create(user_id=self.context['user_id'])

            shipping_address = Address.objects.create(
                user=customer,
                full_name=self.validated_data['full_name'],
                apartment_address=self.validated_data['apartment_address'],
                street_address=self.validated_data.get('street_address', ''),
                postal_code=self.validated_data['postal_code'],
                city=self.validated_data['city'],
                state=self.validated_data['state'],
                country=self.validated_data['country']
            )

            order = Order.objects.create(customer=customer, shipping_address=shipping_address)

            orders_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    unit_price=item.product.price
                )
                for item in CartItem.objects.filter(cart_id=cart_id)
            ]

            OrderItem.objects.bulk_create(orders_items)

            CartItem.objects.filter(pk=cart_id).delete()

            return order

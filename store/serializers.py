from rest_framework import serializers
from .models import Product, Category, Size, Cart, CartItem


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size']


class ProductSerializer(serializers.ModelSerializer):
    sizes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Size.objects.all()
    ) 

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'slug', 'description', 'details', 'price', 'stock', 'sizes', 'created_at']
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
from rest_framework import serializers
from .models import Product, Category, Size


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


from django.shortcuts import render
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin

from .serializers import ProductSerializer, CategorySerializer, SizeSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .models import Product, Category, Size, Cart, CartItem
from .filters import ProductFilter
from .pagination import DefaultPagination

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    pagination_class = DefaultPagination
    lookup_field = 'slug'


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(products_count=Count('products')).all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class SizeViewSet(ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer 

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
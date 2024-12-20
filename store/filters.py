from django_filters.rest_framework import FilterSet, CharFilter
from django_filters import rest_framework as filters
from .models import Product



class ProductFilter(FilterSet):
    sizes = CharFilter(field_name='sizes__size', method='filter_by_sizes')

    class Meta:
        model = Product
        fields = {
            'category':['exact'],
            'price':['gt','lt']
        }

    def filter_by_sizes(self, queryset, name, value):
        sizes = value.split(',')
        return queryset.filter(sizes__size__in=sizes).distinct()
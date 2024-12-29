from urllib.parse import urlencode
from django.contrib import admin
from .models import Category, Customer, Order, OrderItem, Product, ProductImage, Address
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
# Register your models here.


class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    prepopulated_fields = {'slug': ['name']}
    inlines = [ProductImageInline]
    actions = ['clear_stock']
    list_display = ['name', 'price', 'stock_status', 'stock', 'category_name']
    list_editable = ['price', 'stock']
    list_per_page = 10
    search_fields = ['name']
    list_select_related = ['category']
    list_filter = ['category', 'updated_at']
    filter_horizontal = ['sizes']

    def category_name(self, product):
        return product.category.name

    @admin.action(description='Clear Stock')
    def clear_stock(self, request, queryset):
        updated_count = queryset.update(stock=0)
        self.message_user(request, f'{updated_count} products were successfully updated', level='Success') 

    @admin.display(ordering='stock')
    def stock_status(self, product):
        if(product.stock < 10):
            return 'Low'
        return 'Ok'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'orders']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name', 'user__last_name', 'phone_number']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        urls = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            })
        )
        return format_html('<a href="{}"> {} Orders</a>', urls, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']
    autocomplete_fields = ['featured_product']
    prepopulated_fields = {
        'slug':['name']
    }

    @admin.display(ordering='products_count')
    def products_count(self, category):
        urls = (
            reverse('admin:store_product_changelist')
            + '?'
            +urlencode({
                'category_id': str(category.id)
            })
        )
        return format_html('<a href="{}">{} Products </a>', urls, category.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )
    
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min = 1
    max = 10
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer', 'payment_status', 'shipping_address_link']
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']

    def shipping_address_link(self, obj):
        if obj.shipping_address:
            link = reverse("admin:store_address_change", args=[obj.shipping_address.id])
            return format_html('<a href="{}">{}</a>', link, obj.shipping_address)
        return "-"
    shipping_address_link.short_description = 'Shipping Address'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'size', 'quantity', 'unit_price', 'created_at']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'apartment_address', 'street_address', 'city', 'postal_code', 'state', 'country']
    
from . import views 
from rest_framework_nested import routers
from django.urls import path

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)
router.register('sizes', views.SizeViewSet, basename='size')
router.register('carts', views.CartViewSet, basename='cart')
router.register('customer', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='order')
router.register('address', views.AddressViewSet, basename='address')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('images',views.ProductImageViewSet,basename='product-images')


cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('products/newin/', views.ProductViewSet.as_view({'get': 'list'}), name='product-newin'),
]

urlpatterns = router.urls + cart_router.urls + product_router.urls
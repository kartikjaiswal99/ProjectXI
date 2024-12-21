from . import views 
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)
router.register('sizes', views.SizeViewSet, basename='size')
router.register('carts', views.CartViewSet, basename='cart')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-item')


urlpatterns = router.urls + cart_router.urls
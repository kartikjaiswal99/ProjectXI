from . import views 
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)
router.register('sizes', views.SizeViewSet, basename='size')

urlpatterns = router.urls
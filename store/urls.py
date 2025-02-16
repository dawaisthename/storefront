from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductsViewSet)
router.register('collections', views.CollectionViewSet)  # Fixed typo in 'collections'

# Create a nested router for 'reviews' under 'products'
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# Combine both routers' URLs
urlpatterns = router.urls + products_router.urls

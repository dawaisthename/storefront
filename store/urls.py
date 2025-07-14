from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

# print(router)
router.register('products', views.ProductsViewSet,basename='products')
router.register('collections', views.CollectionViewSet)  # Fixed typo in 'collections'
router.register('orders',views.OrderViewSet)
router.register('customers',views.CustomerViewSet)
router.register('carts',views.CartViewSet,basename='carts')

# Create a nested router for 'reviews' under 'products'
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart') 
collection_router = routers.NestedDefaultRouter(router,'collections',lookup='collections')
products_router.register('images',views.ProductsImageViewSet,basename='products-image')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
collection_router.register('images',views.CollectionFeatureImageViewSet,basename='collection-feature-image')
cart_router.register('cartitems',views.CartItemViewSet,basename='cart-item')
# cart_router.register('items', views.CartItemViewSet, basename='cart-items')
urlpatterns = router.urls + products_router.urls+cart_router.urls+collection_router.urls

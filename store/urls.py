from django.urls import path
from . import views
urlpatterns = [
    path('products/',views.products_list),
    path('products/<int:pk>/',views.product_detail),
    path('collections/',views.collection_list),
    path('collections/<int:pk>/',views.collection_detail,name='collection_detail'),
    path('customers/',views.customer_list),
    path('customers/<int:pk>',views.customer_detail,name='customer_detail'),
    path('orders/',views.orders_list),
    
]
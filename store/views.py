from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from .Filters import ProductFilter
from .models import Product,Collection,Customer,Order,OrderItem,Review,Cart,CartItem
from .serializers import ProductSerializer,CollectionSerializer,CustomerSerializer,OrderSerializer,ReviewsSerializer,CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartitemSerializer

#using ModelViewsets
class ProductsViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('reviews').select_related('Collection').all()
    def get_serializer_context(self):
        return {'request':self.request}
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    # handling the filtiration
    filterset_class = ProductFilter
    ordering_fields = ['unit_price']

    search_fields = ['title']
    #customizing the generic view
    def destroy(self,request,*args,**kwargs): 
        #it could also be handled in another way
        if OrderItem.objects.filter(Product_id =kwargs["pk"] ).cnt()>0:
            return Response({'error':'product can not be deleted because it is associated with order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request,*args,**kwargs)
 
class CollectionViewSet(ModelViewSet): 
    queryset = Collection.objects.annotate(product_count=Count('product'))
    serializer_class = CollectionSerializer

    def destroy(self,request,pk):
        #good method to get the instance
        collection = self.get_object()

        if collection.product_set.count()>0:
            return Response({'error':'the collection have a related product in it'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
       
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related('customer').annotate(orders_item = Count('orderitem'))
    def get_serializer_context(self):
        return {'request':self.request}


class CustomerViewSet(ModelViewSet):
    
    queryset = Customer.objects.annotate(orders_count = Count('order'))
    serializer_class =CustomerSerializer
    def get_serializer_context(self):
        return {'request':self.request}

    
class ReviewViewSet(ModelViewSet):

    serializer_class = ReviewsSerializer
    #have to override this method cause it is returning the whole review not the specific one for that product
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])

    def get_serializer_context(self):
        print(self.kwargs)
        return {'product_id':self.kwargs['product_pk'],'request':self.request} #reading and sending the product id from the url
    

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset  = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    # lookup_field = 'cart_id'
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}
    #using different serializer based on the request being made
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer #sending only the product id and the quantity
        elif self.request.method == 'PATCH':
            return UpdateCartitemSerializer
        return CartItemSerializer #getting the info about the items including the totla price

    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
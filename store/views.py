
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .Filters import ProductFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Product,Collection,Customer,Order,OrderItem,Review
from .serializers import ProductSerializer,CollectionSerializer,CustomerSerializer,OrderSerializer,ReviewsSerializer

#using ModelViewsets
class ProductsViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('reviews').select_related('Collection').all()
    def get_serializer_context(self):
        return {'request':self.request}
    filter_backends = [DjangoFilterBackend]
    # handling the filtiration
    filterset_class = ProductFilter
    #customizing the generic view
    def destroy(self,request,*args,**kwargs): 
        #it could also be handled in another way
        if OrderItem.objects.filter(Product_id =kwargs["pk"] ).count()>0:
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
       
class OrderList(ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related('customer').annotate(orders_item = Count('orderitem'))
    def get_serializer_context(self):
        return {'request':self.request}
class OrderDetail(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.select_related('customer').annotate(orders_item = Count('orderitem'))
    serializer_class = OrderSerializer
    

#a view for the customer
@api_view(['GET','POST'])
def customer_list(request):
    if request.method == 'GET':
        customer = Customer.objects.annotate(orders_count = Count('order'))
        serializer = CustomerSerializer(customer,many=True,context={'request':request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

@api_view(['GET','PUT','DELETE'])
def customer_detail(request,pk):     
    customer = get_object_or_404(Customer.objects.annotate(orders_count =Count('order')),pk = pk)
    if request.method =='GET':
        serializer= CustomerSerializer(customer)
        return Response(serializer.data)
    elif request.method =='PUT':
        serializer = CustomerSerializer(customer,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        customer.delete()
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewsSerializer
    #have to override this method cause it is returning the whole review not the specific one for that product
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])

    def get_serializer_context(self):
        print(self.kwargs)
        return {'product_id':self.kwargs['product_pk'],'request':self.request} #reading and sending the product id from the url
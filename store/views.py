
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product,Collection,Customer,Order
from .serializers import ProductSerializer,CollectionSerializer,CustomerSerializer,OrderSerializer
# Create your views here.

@api_view(['GET','POST'])
def products_list(request):
    if request.method == 'GET':
        product = Product.objects.select_related('Collection').all()
        serializer = ProductSerializer(product,many=True,context={'request':request}) #applied to every instance of the model
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer  = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
 
@api_view(['GET','PUT','DELETE'])
def product_detail(request,pk):
    product = get_object_or_404(Product,pk = pk)
    if request.method =='GET':
        serializer = ProductSerializer(product) #serializer also handles a single instnace in addition to a queryset
        return Response(serializer.data)
    elif request.method =="PUT":
        serializer = ProductSerializer(product,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data) #returns the updated object 
     #to update a partial attributes
    elif request.method == 'PATCH':
        serializer = ProductSerializer(product,data=request.data,partial = True)  # Allow partial updates
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    #to delete a product
    elif request.method == 'DELETE':
        if product.orderitems.count()>0:
            return Response({'error':'product can not be deleted because it is associated with order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    return Response(serializer.data)

@api_view(['GET','POST'])
def collection_list(request):
    if request.method == 'GET':
        collection = Collection.objects.annotate(product_count=Count('product'))
        serializer = CollectionSerializer(collection,many=True)
        return Response(serializer.data) 
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
@api_view(['GET','PUT','DELETE'])
def collection_detail(request,pk):
    collection = get_object_or_404(Collection.objects.annotate(product_count=Count('product')),pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
        
    elif request.method =='DELETE':
        if collection.product_set.count()>0:
            return Response({'error':'the collection have a related product in it'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



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
#a view for the order
@api_view(['GET','POST'])
def orders_list(request):
    if request.method == 'GET':
        order= Order.objects.select_related('customer').annotate(orders_item = Count('orderitem'))
        serializer = OrderSerializer(order,many=True,context={'request':request})
        print(serializer.data)
        return Response(serializer.data)
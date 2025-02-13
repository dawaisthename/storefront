#convert the model instance to a dictionary
from rest_framework import serializers
from decimal import Decimal
from .models import Collection,Product,Customer,Order

class CollectionSerializer(serializers.ModelSerializer):
  
    product_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']


class ProductSerializer(serializers.ModelSerializer): #this modelserialzer has save  method to create and update 
    #using a modelserializer
    class Meta:
        model = Product
        fields =['id','title','slug','inventory','description','unit_price','price_with_tax','Collection']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)
    # price = serializers.DecimalField(max_digits=6,decimal_places=2)
    # price = serializers.DecimalField(max_digits=6,decimal_places=2,source ='unit_price') #telling django where to refer since the fields name mismatch
    price_with_tax= serializers.SerializerMethodField(method_name='calculate_tax')
    #creating a Relationship serializer
    # collection = serializers.StringRelatedField(source= "Collection")
    #using a hyperlink
    # Collection = serializers.HyperlinkedRelatedField(queryset = Collection.objects.all(),view_name= "collection_detail")
    #creating a custom serializer fields
    def calculate_tax(self,product): #passing the instance of the object as a parameter
        return product.unit_price* Decimal(1.1)

    #how to override the create and update method of the serializer
    # #just a show off
    #the save method will call one of this method depending on the state of the serializer
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other_attributes = 1
    #     product.save()
    #     return product
    # def update(self, instance, validated_data):
    #     instance.unit_price  = validated_data.get('unit_price') #let's say we want to update the price
    #     instance.save()
    #     return instance

#making a serialzer for the customer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields=  ['last_name','first_name','orders_count']
    orders_count = serializers.IntegerField(read_only= True)

class OrderSerializer(serializers.ModelSerializer):
    orders_item = serializers.IntegerField(read_only=True)
    # customer = serializers.StringRelatedField()
    customer = serializers.HyperlinkedRelatedField(queryset = Customer.objects.all(),view_name= "customer_detail")
    class Meta:
        model = Order
        fields = ['payment_status','placed_at','orders_item','customer']
    
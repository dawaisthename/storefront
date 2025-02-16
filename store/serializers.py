#convert the model instance to a dictionary
from rest_framework import serializers
from decimal import Decimal
from .models import Collection,Product,Customer,Order,Review

class CollectionSerializer(serializers.ModelSerializer):
  
    product_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']


class ProductSerializer(serializers.ModelSerializer): #this modelserialzer has save  method to create and update 
    #using a modelserializer

    reviews = serializers.StringRelatedField(many = True)
    class Meta:
        model = Product
        fields =['id','title','slug','inventory','description','unit_price','price_with_tax','Collection','reviews']
    
    price_with_tax= serializers.SerializerMethodField(method_name='calculate_tax')
    #using a hyperlink
    Collection = serializers.HyperlinkedRelatedField(queryset = Collection.objects.all(),view_name= "collection-detail")
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
        fields = ['id','payment_status','placed_at','orders_item','customer']
    
class ReviewsSerializer(serializers.ModelSerializer):
    product= serializers.HyperlinkedRelatedField(view_name ='product-detail',read_only=True) #no need to include the queryset because it's fetching is handled another way by reading its id from the url
    class Meta:
        model = Review
        fields = ['id','name','description','product']
    
    #overriding the creation of thre review
    def create(self, validated_data):
        product_id  = self.context.get('product_id') #read the product id from the context
        return Review.objects.create(product_id=product_id,**validated_data)

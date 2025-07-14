#convert the model instance to a dictionary
from rest_framework import serializers
from decimal import Decimal
from .models import Collection,Product,Customer,Order,Review,Cart,CartItem,ProductImage,CollectionFeaturedImage
from django.utils.text import slugify


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields =['id','image','uploaded_at']
class ProductSerializer(serializers.ModelSerializer): #this modelserialzer has save  method to create and update 
    #using a modelserializer
    images = ProductImageSerializer(many=True,read_only=True)
    reviews = serializers.StringRelatedField(many = True,read_only=True)
    
    class Meta:
        model = Product
        fields =['id','title','slug','inventory','description','unit_price','price_with_tax','collection','reviews','images']
    
    price_with_tax= serializers.SerializerMethodField(method_name='calculate_tax')
    #using a hyperlink
    # Collection = serializers.HyperlinkedRelatedField(queryset = Collection.objects.all(),view_name= "collection-detail")
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    #creating a custom serializer fields
    def calculate_tax(self,product): #passing the instance of the object as a parameter
        return product.unit_price* Decimal(1.1)
    def generate_unique_slug(self,title):
        base_slug = slugify(title)
        slug = base_slug
        index = 1
        while Product.objects.filter(slug=slug).exists():
            index+=1
            slug=f"{base_slug} -- {index}"
        return slug
    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug']=self.generate_unique_slug(validated_data['title'])
        return super().create(validated_data)
    #we have to override the update method too just incase the title is updated and the slug has to as well
    def update(self, instance, validated_data):
        if validated_data.get('title') and not validated_data.get('slug'):
            validated_data['slug'] =self.generate_unique_slug(validated_data['title'])
        return super().update(instance, validated_data)
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
class CollectionFeatureImageSerializer(serializers.ModelSerializer):
    class Meta:
        model =CollectionFeaturedImage
        fields =['id','image','uploaded_at','collection']

class CollectionSerializer(serializers.ModelSerializer):
  
    product_count = serializers.IntegerField(read_only=True)
    products = ProductSerializer(read_only=True,many=True,source='product_set')
    feature_image = CollectionFeatureImageSerializer(many = True,read_only=True)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count','products','feature_image']


#making a serialzer for the customer
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    # orders_count = serializers.IntegerField(read_only= True)
    class Meta:
        model = Customer
        fields=  ['id','user_id','phone','membership','birth_date']

class OrderSerializer(serializers.ModelSerializer):
    orders_item = serializers.IntegerField(read_only=True)
    # customer = serializers.StringRelatedField()
    customer = serializers.HyperlinkedRelatedField(queryset = Customer.objects.all(),view_name= "customer-detail")
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
    
# avoid unnecessary attributes to show
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    def get_total_price(self,cart_item):
        return cart_item.quantity * cart_item.product.unit_price
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']
class AddCartItemSerializer(serializers.ModelSerializer):
   product_id = serializers.IntegerField() #has to be set explicitly
   #the parameters has to be validated before being saved
   def validate_product_id(self,value):
        if not Product.objects.filter(pk = value).exists():
            raise serializers.ValidationError('No Product with the given id')
        return value
   #the save method of the modelserializer has to be override based on the requirements
   def save(self, **kwargs):
        
        cart_id  = self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:   
            cart_item= CartItem.objects.get(cart_id=cart_id,product_id=product_id) #updating the cartitem
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)
        return self.instance
             
   class Meta:
       model = CartItem
       fields = ['id','product_id','quantity'] 
class UpdateCartitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # items = CartItemSerializer(many=True)   
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    def get_total_price(self,cart):
       return sum([item.quantity * item.product.unit_price for item in cart.items.all()]) 
    class Meta:
        model = Cart
        fields = ['id','items','created_at','total_price']


from django.conf import settings
from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator
from uuid import uuid4
class Promotion(models.Model):
    discription = models.CharField(max_length=255)
    discount = models.FloatField()
class Collection(models.Model):
    title = models.CharField(max_length=255)
    #the circular dependency is handled
    featured_product = models.ForeignKey('Product',on_delete=models.SET_NULL,null = True,related_name='+',blank=True) 

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']
class CollectionFeaturedImage(models.Model):

    image =models.ImageField(upload_to='store/collections/images')
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE,related_name='feature_image')
    def __str__(self):
        return f"image of {self.collection.title}"
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True)
    description = models.TextField(null= True,blank=True)#make the null at  the database and the admin form
    unit_price = models.DecimalField(max_digits=6,decimal_places=2,validators=[MinValueValidator(1)]) #make sure the price is postive
    inventory = models.IntegerField(validators=[MinValueValidator(1)]) #make sure the price the attribute stays positive
    last_update = models.DateTimeField(auto_now=True)
    #guarantee no product deleted when the collection is deleted
    collection = models.ForeignKey(Collection,on_delete=models.PROTECT) #many to one relation between the collection and the product 
    #product could have a multiple promotion
    promotions = models.ManyToManyField(Promotion,blank=True) #since it is many to many if nothing is selected it will be set to empty
    

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/prdoucts/images')  # adjust path as needed
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
      return f'Image of "{self.product.title}"'

class Customer(models.Model):
    MEMEBERSHIP_BRONZE = 'B'
    MEMEBERSHIP_SILVER = 'S'
    MEMEBERSHIP_GOLD = 'G'
    MEMEBERSHIP_CHOICES = [
        (MEMEBERSHIP_BRONZE,'Bronze'),
        (MEMEBERSHIP_SILVER,'Silver'),
        (MEMEBERSHIP_GOLD,'Gold'),
    ]


    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(choices=MEMEBERSHIP_CHOICES,max_length=1,default=MEMEBERSHIP_BRONZE)
    user= models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name}  {self.user.last_name}' 
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering = ['user__first_name','user__last_name'] #refrencing the user model

   
class Order(models.Model):
    #a good habit to use variables to store the choices
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS = [
        (PAYMENT_STATUS_PENDING,'Pending'),
        (PAYMENT_STATUS_COMPLETE,'Complete'),
        (PAYMENT_STATUS_FAILED,'Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True) #filled every time object created
    payment_status = models.CharField(max_length=1,choices=PAYMENT_STATUS,default=PAYMENT_STATUS_PENDING)
    #make sure the order never deleted when the customer is deleted
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT)

    class Meta:
        permissions =[
            ('cancel_order','Can Cancel Order')
        ]
#when the products are ordered
class OrderItem(models.Model):
    
    order= models.ForeignKey(Order,on_delete=models.PROTECT)
    #one product could be ordered many times
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name='orderitems')
    quantity = models.PositiveBigIntegerField() #make sure negative numbers won't stored
    unit_price = models.DecimalField(max_digits=6,decimal_places=2) #the latest price
    
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    #the relation between the customer and the adress
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,primary_key=True) #makes sure it is one to one
    zip_code = models.CharField(max_length=20)  # ZIP code stored as a stringj
class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        unique_together = [['user']]
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    ) #make sure negative numbers won't stored

    class Meta:
        #to make sure only one instance of a product is store only the quantity increase 
        unique_together= [['cart','product']]
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Review of "{self.product.title}" by {self.name} on {self.date}'

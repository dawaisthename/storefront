from django.db import models
from django.core.validators import MinValueValidator
class Promotion(models.Model):
    discription = models.CharField(max_length=255)
    discount = models.FloatField()
class Collection(models.Model):
    title = models.CharField(max_length=255)
    #the circular dependency is handled
    featured_product = models.ForeignKey('Product',on_delete=models.SET_NULL,null = True,related_name='+') 

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(default='')
    description = models.TextField(null= True,blank=True)#make the null at  the database and the admin form
    unit_price = models.DecimalField(max_digits=6,decimal_places=2,validators=[MinValueValidator(1)]) #make sure the price is postive
    inventory = models.IntegerField(validators=[MinValueValidator(1)]) #make sure the price the attribute stays positive
    last_update = models.DateTimeField(auto_now=True)
    #guguarantee no product deleted when the collection is deleted
    Collection = models.ForeignKey(Collection,on_delete=models.PROTECT) #many to one relation between the collection and the product 
    #product could have a multiple promotion
    Promotions = models.ManyToManyField(Promotion,blank=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']
class Customer(models.Model):
    MEMEBERSHIP_BRONZE = 'B'
    MEMEBERSHIP_SILVER = 'S'
    MEMEBERSHIP_GOLD = 'G'
    MEMEBERSHIP_CHOICES = [
        (MEMEBERSHIP_BRONZE,'Bronze'),
        (MEMEBERSHIP_SILVER,'Silver'),
        (MEMEBERSHIP_GOLD,'Gold'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True)
    membership = models.CharField(choices=MEMEBERSHIP_CHOICES,max_length=1,default=MEMEBERSHIP_BRONZE)

    def __str__(self):
        return f'{self.first_name}  {self.last_name}'
    
    class Meta:
        ordering = ['first_name','last_name']

   
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


#when the products are ordered
class OrderItem(models.Model):
    order= models.ForeignKey(Order,on_delete=models.PROTECT)
    #one product could be ordered many times
    Product = models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField() #make sure negative numbers won't stored
    unit_price = models.DecimalField(max_digits=6,decimal_places=2) #the latest price
    
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    #the relation between the customer and the adress
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,primary_key=True) #makes sure it is one to one
    zip_code = models.CharField(max_length=20)  # ZIP code stored as a stringj
class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField() #make sure negative numbers won't stored

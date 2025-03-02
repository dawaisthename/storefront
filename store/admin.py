from django.contrib import admin,messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from .models import Collection,Product,Customer,Order,OrderItem,Cart,CartItem
from django.utils.html import format_html,urlencode
from django.urls import reverse

#custom filter 
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    def lookups(self, request, model_admin):
        return [
            ('<10','Low'), #the actual value and the human redable 

        ]
    def queryset(self, request, queryset):
        if self.value() == '<10': #returns a string 
           return queryset.filter(inventory__lt =10)


class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['Collection']
    prepopulated_fields = {
        'slug':['title']
    }
  
    actions =['clear_inventory']
    search_fields = ['title']
    list_display = ['title', 'unit_price','inventory','inventory_status','collection_title']
    list_select_related = ['Collection']
    list_filter = ['Collection','last_update',InventoryFilter]
    list_editable = ['unit_price']
    list_per_page = 10
    #adding a computed column
    @admin.display(ordering = 'inventory') #use the inventory attriute to sort the inventory_status column
    def inventory_status(self,product): 
        if product.inventory <10:
            return 'Low'
        return 'ok'
    def collection_title(self,product):
        
        return product.Collection.title
    #creating a custom action
    @admin.action(description='ClearInventory')
    def clear_inventory(self,request,queryset):
        updated_count =queryset.update(inventory = 0) #returns the number of updated records
        self.message_user(request,f'{updated_count} Products were successfully updated.',
                          messages.ERROR)
#manage the items in the order
#by editing the children inline
class OrderItemInline(admin.StackedInline):
    autocomplete_fields = ['Product']   
    model = OrderItem
    min_num = 1
    max_num =10
    extra= 0

class OrderAdmin(admin.ModelAdmin): 
    inlines = [OrderItemInline] #to manage the orderitems in the order class
    list_display = ['customer','placed_at','payment_status']
    list_select_related = ['customer']

    def customer_name(self,customer):
        return Order.customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership','orders_count']
    list_editable = ['membership']
    search_fields = ['first_name__istartswith']    
    ordering = ['user__first_name','user__last_name']
    list_select_related = ['user']
    @admin.display
    def orders_count(self,customer):
        #prodviding a link to other page
        url = (reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id':str(customer.id )
            })          
                )
        return format_html('<a href="{}" >{}</a>',url,customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count = Count('order'))
    
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']
    @admin.display(ordering='products_count')
    def products_count(self,collection):
        #providing a link to other page
        url = (reverse('admin:store_product_changelist')
               + '?'
                + urlencode({
                    'Collection__id':str(collection.id )
                })          
                   )
        return format_html('<a href="{}" >{}</a>',url,collection.products_count)
        # return collection.products_count #will call the overridin method of the queryset
    def get_queryset(self, request): #overriding the base queryset 
        return super().get_queryset(request).annotate(products_count = Count('product') )
    
admin.site.register(Product,ProductAdmin)
admin.site.register(Customer,CustomerAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Collection,CollectionAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
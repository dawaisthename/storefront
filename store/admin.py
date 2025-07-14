from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

from .models import (
    Collection, Product, Customer,
    Order, OrderItem, Cart, CartItem,
    ProductImage,CollectionFeaturedImage
)

# ---------- Custom Filters ----------

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [('<10', 'Low')]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

# ---------- Inline Models ----------

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1

#     # Optional: Show image thumbnail preview in admin
#     readonly_fields = ['image_preview']
    
#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="100" style="object-fit:contain;" />', obj.image.url)
#         return ""
#     image_preview.short_description = 'Preview'

class OrderItemInline(admin.StackedInline):
    autocomplete_fields = ['product']
    model = OrderItem
    min_num = 1
    max_num = 10
    extra = 0

# ---------- Product Admin ----------

class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    # inlines = [ProductImageInline]

    actions = ['clear_inventory']
    search_fields = ['title']
    list_display = ['title', 'unit_price', 'inventory', 'inventory_status', 'collection_title']
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_editable = ['unit_price']
    list_per_page = 10

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        return 'Low' if product.inventory < 10 else 'OK'

    def collection_title(self, product):
        return product.collection.title

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} Products were successfully updated.',
            messages.ERROR
        )

# ---------- Order Admin ----------

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['customer', 'placed_at', 'payment_status']
    list_select_related = ['customer']

# ---------- Customer Admin ----------

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    search_fields = ['first_name__istartswith']
    ordering = ['user__first_name', 'user__last_name']
    list_select_related = ['user']

    @admin.display
    def orders_count(self, customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({'customer__id': str(customer.id)})
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count('order'))

# ---------- Collection Admin ----------

class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id': str(collection.id)})
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))

# ---------- Model Registration ----------

admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ProductImage)
admin.site.register(CollectionFeaturedImage)

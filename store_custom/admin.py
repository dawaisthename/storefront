from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product

# A custom inline to handle the coupling
class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem

# Corrected Custom Product Admin
class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]  # Ensure this is a list

# Unregister and register the admin
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)

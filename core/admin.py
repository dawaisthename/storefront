from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2","email","first_name","last_name"),
            },
        ),
    )
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

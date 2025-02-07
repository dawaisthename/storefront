from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
from tags.models import TaggedItem
from store.models import Order,Customer,Collection
from django.contrib.contenttypes.models import ContentType
from django.db.models import Value,Count
from django.db.models.functions import Concat

# Create your views here.
def Test(request):
    # collection = Collection.objects.get(pk=11)
    # collection.title = 'games'
    # # collection.featured_product = Product(id =1)
    # collection.save()
    Collection.objects.filter(pk=1).update(title='video games') #object has to be filtered first before updated
    return render(request,'home.html')
    



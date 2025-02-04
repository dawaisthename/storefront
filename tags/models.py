from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
#creating an apps model that is not dependent on other apps
#so that we could also us this app for another projects too

class Tag(models.Model):
    label = models.CharField(max_length=255)

class TaggedI(models.Model):
    #what tag applied to what object
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)
    #we need the type of the object(product,video,article)
    #we also need the id of it
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey()


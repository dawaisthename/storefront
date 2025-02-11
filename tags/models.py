from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
#creating an apps model that is not dependent on other apps
#so that we could also us this app for another projects too



# creating a class manager

class TaggedItemManager(models.Manager):
    def get_tags_for(self,obj_type,obj_id): #overriding the method
        content_type = ContentType.objects.get_for_model(obj_type)
        return TaggedItem.objects.select_related('tag').filter(content_type = content_type,object_id =obj_id)

class Tag(models.Model):
    label = models.CharField(max_length=255)
    def __str__(self):
        return self.label

#one tag could be used by many products
class TaggedItem(models.Model):
    objects= TaggedItemManager() #using the customized object manager
    #what tag applied to what object

    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)
    #we need the type of the object(product,video,article)
    #we also need the id of it
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey()


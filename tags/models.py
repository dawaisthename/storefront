from django.db import models
#creating an apps model that is not dependent on other apps
class Tag(models.Model):
    label = models.CharField(max_length=255)

class TaggedItme(models.Model):
    #what tag applied to what object
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)

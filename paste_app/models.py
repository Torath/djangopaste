from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Paste(models.Model):
    content=models.CharField(max_length=500000)
    url=models.CharField(max_length=32)
    author=models.ForeignKey(User,on_delete=models.CASCADE,default=666)
    delete_after_read=models.BooleanField(default=False)
    delete_timestamp = models.DateTimeField(null=True,blank=True)

class UserProfileInfo(models.Model):
    user=models.OneToOneField(User,unique=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


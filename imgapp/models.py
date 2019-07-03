##@package models
#
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

## User Profile 
# 
# One to One reationship with the Django User model. So, the fields of the User models can be used direclty.\n
# Can add extra model fields if needed.
class Profile(models.Model) :
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    company = models.CharField(max_length=50)
    

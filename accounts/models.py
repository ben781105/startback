from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=100,unique=True,null=True,blank=True)
    client =models.BooleanField(default=True)

    def __str__(self):
     return self.username
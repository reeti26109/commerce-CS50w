from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    name=models.CharField(max_length=64)
    description=models.TextField()
    category=models.CharField(max_length=64)
    seller=models.CharField(max_length=64)
    starting_bid=models.IntegerField()
    time=models.DateTimeField(auto_now_add=True)
    image_link=models.CharField(max_length=200, null=True, blank=True, default=None )

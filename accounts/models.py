from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    hostel = models.CharField(max_length=20)
    room_number = models.CharField(max_length=20)

    is_verified = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
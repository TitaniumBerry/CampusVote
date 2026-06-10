from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

import random

# Create your models here.


class User(AbstractUser):
    hostel = models.CharField(max_length=50)
    room_number = models.CharField(max_length=20)

    is_verified = models.BooleanField(default=False)
    has_voted_gensec = models.BooleanField(default=False)
    has_voted_president = models.BooleanField(default=False)

    email = models.EmailField(unique=True)

    # Email for login
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username", "hostel", "room_number"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def has_voted_all(self):
        return self.has_voted_gensec and self.has_voted_president


class OTPVerification(models.Model):
    

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,    # delete otp after user is deleted
        related_name = "otp",
    )

    code = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)

    EXPIRY_MINS = 5

    def is_expired(self):
        #true if OTP is older than expiry mins
        expiry_time = self.created_at + timezone.timedelta(minutes=self.EXPIRY_MINS)

        return timezone.now() > expiry_time

    
    @classmethod
    def generate_for(cls, user):
        # creates or replaces otp for user

        # deletes old otp before creation

        cls.objects.filter(user = user).delete()
        code = str(random.randint(1000, 9999))

        return cls.objects.create(user=user, code=code)

    def __str__(self):
        return f"OTP for {self.user.email} (expires in {self.EXPIRY_MINS} mins)"

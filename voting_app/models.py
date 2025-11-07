from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_data")
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    phone = models.CharField(max_length=15, unique=True, verbose_name="Phone Number")
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Gender")
    address1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    address2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address Line 2")
    city = models.CharField(max_length=100, verbose_name="City")
    state = models.CharField(max_length=100, verbose_name="State")
    postcode = models.CharField(max_length=20, verbose_name="Postcode/ZIP")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.city}, {self.state} - {self.postcode}"

    class Meta:
        verbose_name = "User Data"
        verbose_name_plural = "User Data"

        ordering = ['-created_at']


class CustomUser(models.Model):
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    is_voter = models.BooleanField(default=True)
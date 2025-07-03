from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager

ACCOUNT_TYPE = (
    ("SYSTEM", "System User"),
    ("CUSTOMER", "Customer"),
    ("MOVER", "Mover")
)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        "Email Address",
        unique=True,
    )
    
    role = models.CharField("Account Type", choices=ACCOUNT_TYPE, default='CUSTOMER')
    is_mover = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='user/profile_images/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=(("male", "Male"), ("female", "Female")), blank=True,  null=True)
    dob = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        full_name = super().get_full_name()
        if not full_name:
            full_name = self.email
        return full_name
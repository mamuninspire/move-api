from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import CommonModel
import uuid
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class Customer(CommonModel):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    phone_number = PhoneNumberField(blank=True)
    is_mobile_verified = models.BooleanField(default=False)
    is_whatsapp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email}"

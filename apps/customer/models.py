from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
# from core.models import CommonModel
import uuid

User = get_user_model()


class Customer(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Customer Profile for {self.user.email}"

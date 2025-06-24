from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from core.models import CommonModel

User = get_user_model()

mm_yy_validator = RegexValidator(
    regex=r'^(0[1-9]|1[0-2])\/\d{2}$',
    message="Date must be in MM/YY format"
)


class PaymentType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Payment Type"
        verbose_name_plural = "Payment Types"


class PaymentMethod(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)
    expire_date = models.CharField(max_length=5, validators=[mm_yy_validator], help_text="Enter date in MM/YY format")
    cvv = models.CharField(max_length=3, validators=[RegexValidator(r'^\d{3}$', message="Enter exactly 3 digits.")], help_text="123")
    card_holder_name = models.CharField(max_length=100, blank=False, null=False)


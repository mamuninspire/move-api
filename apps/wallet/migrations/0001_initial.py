# Generated by Django 5.2.1 on 2025-06-17 08:32

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Payment Type',
                'verbose_name_plural': 'Payment Types',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card_number', models.CharField(max_length=20)),
                ('expire_date', models.CharField(help_text='Enter date in MM/YY format', max_length=5, validators=[django.core.validators.RegexValidator(message='Date must be in MM/YY format', regex='^(0[1-9]|1[0-2])\\/\\d{2}$')])),
                ('cvv', models.CharField(help_text='123', max_length=3, validators=[django.core.validators.RegexValidator('^\\d{3}$', message='Enter exactly 3 digits.')])),
                ('card_holder_name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('payment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.paymenttype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

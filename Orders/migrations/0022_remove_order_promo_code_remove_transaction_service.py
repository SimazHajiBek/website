# Generated by Django 5.1.4 on 2025-03-09 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0021_remove_order_promo_code_order_fee_and_more'),
    ]

    operations = [
        
        migrations.RemoveField(
            model_name='transaction',
            name='service',
        ),
    ]

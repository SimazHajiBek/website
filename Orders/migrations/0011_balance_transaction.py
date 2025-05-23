# Generated by Django 5.1.4 on 2025-01-24 10:13

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0010_alter_cartitem_service_alter_order_service_and_more'),
        ('Users', '0016_remove_creator_average_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('withdrawable_balance', models.PositiveIntegerField(default=0)),
                ('pending_balance', models.PositiveIntegerField(default=0)),
                ('total_balance', models.PositiveIntegerField(default=0)),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='balance', to='Users.creator')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('transaction_type', models.CharField(max_length=50)),
                ('date', models.DateField(auto_now_add=True)),
                ('service', models.CharField(blank=True, max_length=255, null=True)),
                ('current_balance', models.PositiveIntegerField()),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='Users.creator')),
            ],
        ),
    ]

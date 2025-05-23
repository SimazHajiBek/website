# Generated by Django 5.1.4 on 2025-01-26 12:42

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0011_balance_transaction'),
        ('Services', '0006_content_is_portfolio_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='amount',
            new_name='total_price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='service',
        ),
        migrations.RemoveField(
            model_name='order',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='in_progress', max_length=15),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Orders.order')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Services.service')),
            ],
        ),
    ]

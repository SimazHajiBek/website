# Generated by Django 5.1.4 on 2025-03-14 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0032_alter_transaction_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawal',
            name='state',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='PENDING', max_length=20),
        ),
    ]

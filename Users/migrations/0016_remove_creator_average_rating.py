# Generated by Django 5.1.4 on 2025-01-24 10:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0015_remove_service_creator_remove_servicevideo_service_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creator',
            name='average_rating',
        ),
    ]

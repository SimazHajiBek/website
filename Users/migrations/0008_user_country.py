# Generated by Django 5.1.4 on 2024-12-28 22:13

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0007_service_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, null=True),
        ),
    ]

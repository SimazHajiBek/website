# Generated by Django 5.1.4 on 2025-01-02 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0010_servicevideo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='video_file',
        ),
    ]

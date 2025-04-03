from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Creator, Balance
#عند إنشاء Creator جديد (post_save signal)، يتم إنشاء Balance مرتبط به تلقائيًا.



@receiver(post_save, sender=Creator)
def create_balance_for_creator(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(creator=instance)

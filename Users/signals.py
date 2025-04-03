from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Avg
from .models import User, Brand, Creator


@receiver(post_save, sender=User)
def create_brand_or_creator(sender, instance, created, **kwargs):
    """
    Automatically create a Brand or Creator instance when a User is created.
    """
    if created:  # يتم تشغيل الكود عند إنشاء User جديد فقط
        if instance.user_type == 'brand':
            Brand.objects.create(user=instance)
        elif instance.user_type == 'creator':
            Creator.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_brand_or_creator(sender, instance, **kwargs):
    """
    Save the related Brand or Creator when User is saved.
    """
    if hasattr(instance, 'brand'):  # إذا كان هذا الـ User لديه Brand
        instance.brand.save()
    if hasattr(instance, 'creator'):  # إذا كان هذا الـ User لديه Creator
        instance.creator.save()



# # تحديث متوسط التقييم عند إنشاء/تحديث تقييم
# @receiver(post_save, sender=Rating)
# def update_creator_average_rating_on_save(sender, instance, **kwargs):
#     creator = instance.creator
#     # حساب المتوسط الجديد
#     avg_rating = creator.ratings.aggregate(avg=Avg('rating'))['avg'] or 0.0
#     # تحديث الحقل في قاعدة البيانات
#     creator.average_rating = avg_rating
#     creator.save()

# # تحديث متوسط التقييم عند حذف تقييم
# @receiver(post_delete, sender=Rating)
# def update_creator_average_rating_on_delete(sender, instance, **kwargs):
#     creator = instance.creator
#     # حساب المتوسط الجديد
#     avg_rating = creator.ratings.aggregate(avg=Avg('rating'))['avg'] or 0.0
#     # تحديث الحقل في قاعدة البيانات
#     creator.average_rating = avg_rating
#     creator.save()




# post_save Signal: يتم تشغيله بعد حفظ أي سجل في قاعدة البيانات.
# created: يتحقق مما إذا كان هذا السجل قد تم إنشاؤه حديثًا.
# Brand.objects.create و Creator.objects.create: تقوم بإنشاء السجل المرتبط في جدول Brand أو Creator حسب قيمة الحقل user_type.
# hasattr(instance, 'brand'): يتحقق إذا كان لدى المستخدم علاقة مع Brand ويقوم بحفظها.
# hasattr(instance, 'creator'): يتحقق إذا كان لدى المستخدم علاقة مع Creator ويقوم بحفظها.


#عند إنشاء أو تحديث تقييم جديد (Rating):

# يتم تشغيل إشارة post_save.
# تحسب الإشارة متوسط التقييمات الجديدة باستخدام aggregate.
# يتم تخزين النتيجة في الحقل average_rating في الكائن Creator.
# عند حذف تقييم:

# يتم تشغيل إشارة post_delete.
# يتم حساب المتوسط الجديد وتحديث الحقل.

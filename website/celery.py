
import os
from celery import Celery
from celery.schedules import crontab  # ✅ استيراد crontab للجدولة الزمنية

# تحديد إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

# إنشاء كائن Celery وربطه بالمشروع
celery = Celery('website')

# تحميل إعدادات Celery من settings.py
celery.config_from_object('django.conf:settings', namespace='CELERY')

# البحث عن جميع المهام (tasks) داخل التطبيقات المسجلة
celery.autodiscover_tasks()


celery.conf.beat_schedule = {
    'release-pending-payments-everyday': {
        'task': 'orders.tasks.release_pending_payments',
        #'schedule': crontab(hour=0, minute=0),  # تنفيذ المهمة يوميًا الساعة 00:00
        'schedule': crontab(minute='*/1'),  # ✅ تشغيل المهمة كل دقيقة أثناء الاختبار

    },
}
from celery import shared_task
from django.utils import timezone
from .models import Payment

@shared_task
def release_pending_payments():
    """تحويل المدفوعات بعد 14 يومًا إذا لم يتم الإلغاء"""
    now = timezone.now()
    #pending_payments = Payment.objects.filter(payment_status='PENDING', release_date__lte=now)
    five_minutes_ago = now - timedelta(minutes=5)  # ✅ بدلاً من 14 يومًا
    pending_payments = Payment.objects.filter(payment_status='PENDING', release_date__lte=five_minutes_ago)


    for payment in pending_payments:
        transfer_money_to_creator(payment)
        payment.payment_status = 'SUCCESS'
        payment.save()

def transfer_money_to_creator(payment):
    """محاكاة تحويل الأموال إلى مقدم الخدمة (يتم استبدالها بخدمة دفع حقيقية)"""
    creator = payment.order.creator
    creator.wallet_balance += payment.amount  # إضافة المال إلى محفظة الـ Creator
    creator.save()
    print(f"✅ تم تحويل {payment.amount} إلى {creator.name}")

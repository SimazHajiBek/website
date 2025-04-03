from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.response import Response
from uuid import uuid4
from Users.models import Brand, Creator, User
from Services.models import Service
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
'''
Order, Payment, Withdrawal, Transaction, Balance,
Cart, CartItem, Purchase
'''

class Brief(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brief')
    creator_id = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='brief')
    content_requirements = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Brief {self.id} - Budget: {self.budget}"


class PromoCode(models.Model):#تطبيق خصومات على المدفوعات أو المشتريات
    STATUS_DISCOUNT_TYPE = [
        ('fixed', 'Fixed'),
        ('percent', 'Percent'),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)
    code = models.CharField(max_length=50, unique=True)  # كود الخصم
    discount_type = models.CharField(max_length=10, choices=STATUS_DISCOUNT_TYPE, default='fixed')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)  # مقدار الخصم
    is_active = models.BooleanField(default=True)  # هل الكود فعال؟

    def apply_discount(self, total):
        """حساب قيمة الخصم"""
        if self.discount_type == 'fixed':
            return self.discount_amount  # ✅ خصم ثابت
        elif self.discount_type == 'percent':
            return (self.discount_amount / 100) * total  # ✅ خصم نسبة مئوية
        return 0
            
    def __str__(self):
        return f" #{self.code} - {self.discount_amount}"


class Fee(models.Model):#طبيق رسوم إضافية على المدفوعات أو المشتريات مثل رسوم الخدمة أو الضرائب
    id = models.UUIDField(default=uuid4, primary_key=True)
    name = models.CharField(max_length=255)  # اسم الرسوم
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # المبلغ

    def __str__(self):
        return f"{self.amount}"

class Order(models.Model):
#هذا النموذج يمثل الطلب (Order) الذي يتم إنشاؤه في النظام.
#  يحتوي على معلومات عامة عن الطلب، مثل العلامة التجارية (Brand)،
#  والمنشئ (Creator)، والسعر الإجمالي، والحالة، وغيرها.
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='orders')
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='created_orders', null=True,  # 👈 اجعلها اختيارية إذا لم يكن كل طلب يحتاج إلى منشئ
    blank=True)  # الـ Creator
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # السعر الإجمالي
    #ليس من الضروري تخزين total_price في Order لأنه يمكن حسابه من OrderItem.
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')  # حالة الطلب
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ الإنشاء
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True)
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['brand', 'creator']),  # فهرس على حقل brand
            
        ]

    def total_profit(self):
        return sum(item.profit for item in self.items.all())

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def total_cost(self):
        items_total = sum(item.total_price() for item in self.items.all())
        fee_amount = self.fee.amount if self.fee else 0

        discount = 0
        if self.promo_code:
            discount = self.promo_code.apply_discount(items_total)  # ✅ حساب الخصم بناءً على النوع
        
        return max(items_total + fee_amount - discount, 0)  # ✅ منع القيم السالبة

    # items_total: يجمع سعر جميع العناصر.
    # fee_amount: يضيف أي رسوم إضافية إذا وُجدت.

    def __str__(self):
        return f"Order #{self.id} - {self.brand.brand_name}"
    

class OrderItem(models.Model):
#هذا النموذج يمثل الطلب (Order) الذي يتم إنشاؤه في النظام.
#  يحتوي على معلومات عامة عن الطلب، مثل العلامة التجارية (Brand)، والمنشئ (Creator)، والسعر الإجمالي، والحالة،
#  إدارة العناصر التفصيلية لكل طلب.
    id = models.UUIDField(default=uuid4, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")  # الطلب المرتبط
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # الخدمة المرتبطة
    quantity = models.PositiveIntegerField(default=1)  # الكمية
    price = models.DecimalField(max_digits=10, decimal_places=2)  # السعر الفردي 
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ إضافة الأرباح

    def save(self, *args, **kwargs):
        # ✅ احتساب الربح (مثلاً 80% لصانع المحتوى بعد خصم 20% عمولة)
        if not self.profit:
            self.profit = self.price * self.quantity * 0.8  # مثال: 80% لصانع المحتوى
        super().save(*args, **kwargs)

    def total_price(self):
        return self.price * self.quantity  # السعر الإجمالي للعنصر

    class Meta:
        indexes = [
            models.Index(fields=['order', 'service']),  # فهرس على حقل order
        ]

    def __str__(self):
        return f"Item in {self.order}"




class Payment(models.Model):
#نموذج Payment يمثل عملية الدفع المرتبطة بطلب (Order) في نظامك.
#  هذا النموذج 
# يُستخدم لتتبع معلومات الدفع، 
# مثل طريقة الدفع، وحالة الدفع،
#  وتاريخ إنشاء الدفع.
#  إليك شرح مفصل لفائدة
#  كل حقل ودور النموذج بشكل عام:

#هل نربطه مع transaction؟
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('CANCELED', 'Canceled'), # تم الإلغاء
        ('PENDING', 'Pending'),
    ]
    PAYMENT_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('CREDITCARD', 'Credit Card'),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)  # معرف فريد لكل عملية دفع
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='payments')
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(null=True, blank=True)  # تاريخ تحويل الأموال

    def set_release_date(self):
        """ضبط تاريخ التحويل بعد 14 يومًا من الدفع"""
        self.release_date = timezone.now() + timedelta(days=14)
        self.save()

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"



class Withdrawal(models.Model):#لادارة طلبات السحب الخاصة بصناع المحتوى
    STATUS_CHOICES = [
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
    ]

    WITHDRAWAL_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('CREDITCARD', 'Credit Card'),
    ]

    id = models.UUIDField(default=uuid4, primary_key=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.PositiveIntegerField()  # المبلغ المراد سحبه
    withdrawal_method = models.CharField(max_length=50, choices=WITHDRAWAL_CHOICES)
    account_details = models.CharField(max_length=1024)  # بيانات الحساب (إيميل PayPal أو حساب مصرفي)
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    date = models.DateField(auto_now_add=True)  # تاريخ السحب

    def __str__(self):
        return f"Withdrawal #{self.id} - {self.creator.user.email} - {self.state}"


class Balance(models.Model):
#هذا النموذج يمثل رصيد المنشئ، سواء كان قابلًا للسحب أو معلقًا.

    id = models.UUIDField(default=uuid4, primary_key=True)
    creator = models.OneToOneField(Creator, on_delete=models.CASCADE, related_name='balance')
    withdrawable_balance = models.PositiveIntegerField(default=0)  # الرصيد القابل للسحب
    pending_balance = models.PositiveIntegerField(default=0)  # الرصيد المعلق
    # #total_balance  يجب أن يكون @property وليس حقلًا محجوزًا:
    # #لأن الرصيد الإجمالي يتم حسابه دائمًا وليس تخزينه.

    # @property
    # def total_balance(self):
    #     return self.withdrawable_balance + self.pending_balance  # احتساب الرصيد الإجمالي

    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # حفظ الرصيد في قاعدة البيانات

    def update_total_balance(self):
        self.total_balance = self.withdrawable_balance + self.pending_balance
        self.save()

    # def save(self, *args, **kwargs):
    #     # تحديث الرصيد قبل الحفظ
    #     self.update_total_balance()
    #     super().save(*args, **kwargs)  # استدعاء الحفظ الأصلي

class Transaction(models.Model):
#هذا النموذج يمثل سجل المعاملات المالية للمنشئين.
#  يُستخدم لتسجيل كل معاملة مالية، سواء كانت إيداعًا أو سحبًا أو مرتبطة بخدمة معينة.
    TRANSACTION_TYPES = [
        ('service', 'Service Income'),
        ('withdraw', 'Paypal Withdraw'),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='transactions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="transactions", blank=True, null=True)
    amount = models.IntegerField()  # يمكن أن يكون موجبًا أو سالبًا
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    date = models.DateField(auto_now_add=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)

class Cart(models.Model):
#ستخدم لإدارة عربات التسوق
    id = models.UUIDField(default=uuid4, primary_key=True)
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name="cart")  # ربط العربة بالمستخدم
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True)
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, blank=True, null=True)

    def apply_promo_code(self, promo_code_str):
        """تطبيق كود الخصم على العربة"""
        try:
            promo = PromoCode.objects.get(code=promo_code_str, is_active=True)
            self.promo_code = promo
            self.save()
            return True
        except PromoCode.DoesNotExist:
            return False  # كود الخصم غير صحيح

    def total_price(self):
        """حساب السعر النهائي بعد تطبيق الخصم والرسوم"""
        items_total = sum(item.total_price() for item in self.items.all())  # ✅ إجمالي المنتجات
        fee_amount = self.fee.amount if self.fee else 0  # ✅ إضافة الرسوم إن وجدت

        discount = 0
        if self.promo_code:
            discount = self.promo_code.apply_discount(items_total)  # ✅ حساب الخصم بناءً على النوع
        
        return max(items_total + fee_amount - discount, 0)  # ✅ منع القيم السالبة

# apply_promo_code() لأن المستخدم يحتاج إلى إدخال كود الخصم أولًا، ثم يتم حفظه في Cart.
# وبعدها يتم استخدام total_price() لحساب السعر النهائي في أي وقت بناءً على الكود المخزن.

   
    def total_items(self):
        #return sum(item.quantity for item in self.items.all())  # ✅ عدد العناصر الإجمالي
        return self.items.count()  # عدد المنتجات

    def __str__(self):
        return f"Cart of {self.brand.user.username}"


#لادارة العربة الخاصة بالbrand والمنتجات الموجودة داخلها

class CartItem(models.Model):
#يُستخدم لإدارة العناصر المضافة إلى العربة
    id = models.UUIDField(default=uuid4, primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ إضافة السعر عند إدخال العنصر

    class Meta:
        unique_together = ('cart', 'service')  # منع تكرار نفس المنتج في العربة

    def save(self, *args, **kwargs):
        # تعيين السعر من الخدمة تلقائيًا عند الحفظ
        if not self.price:
            self.price = self.service.price
        super().save(*args, **kwargs)

    def total_price(self):
        return self.price * self.quantity  # ✅ استخدام السعر المخزن بدل حسابه ديناميكيًا

    def __str__(self):
        return f"{self.quantity} x {self.service.service_name}"


# إضافة عنصر إلى العربة
# عرض محتويات العربة
# إزالة عنصر من العربة
# تحديث كمية العناصر
# إضافة AJAX: لتحديث الكمية وإزالة العناصر بدون إعادة تحميل الصفحة.
# إرسال إشعارات: لتأكيد الدفع أو عند إضافة عنصر جديد.
# حماية بيانات الدفع: باستخدام مكتبة مثل Stripe أو PayPal SDK.

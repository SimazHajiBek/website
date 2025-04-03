from uuid import uuid4
from django.db import models
from django.db.models import Avg
from Users.models import Creator
# Create your models here.


class Service(models.Model):
    PLATFORM_CHOICES = [
        ('Instagram', 'Instagram'),
        ('Facebook', 'Facebook'),
        ('Snapchat', 'Snapchat'),
        ('Tiktok', 'Tiktok'),
        ('Youtube', 'Youtube'),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)
    creator = models.ForeignKey(Creator,on_delete=models.CASCADE,related_name="services")  # ربط الخدمة بالمستخدم من نوع Creator
    service_name = models.CharField(max_length=255, help_text="Name of the service")  # اسم الخدمة
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    video_length = models.PositiveIntegerField(help_text="Length of the video in seconds")  # طول الفيديو بالثواني
    hooks_numbers = models.PositiveIntegerField(help_text="Number of hooks in the video")  # عدد الخطافات
    call_to_action_number = models.PositiveIntegerField(help_text="Number of call-to-actions")  # عدد العبارات التحفيزية
    voice_over = models.BooleanField(default=False, help_text="Does the video include voice-over?")  # هل يحتوي على تعليق صوتي؟
    face_appearing = models.BooleanField(default=False, help_text="Does the video include face appearing?")  # هل يظهر الوجه؟
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Syrian pounds")
    
    created_at = models.DateTimeField(auto_now_add=True)  # يخزن تاريخ ووقت إنشاء السجل
    updated_at = models.DateTimeField(auto_now=True)  # يخزن تاريخ ووقت آخر تعديل للكائن.

    class Meta:
        indexes = [
            models.Index(fields=['creator', 'platform']),  # فهرس على الحقل creator
        ]
    
    def __str__(self):
        return f"{self.service_name} by {self.creator}"
#hook: هو العنصر أو الجزء في بداية الفيديو الذي يجذب انتباه المشاهد بسرعة. عادةً، يتم استخدام الـ Hook في أول 3-5 ثوانٍ من الفيديو، ويكون مصممًا لجعل المشاهد يشعر بالاهتمام أو الفضول لمواصلة المشاهدة.
#call to action:  هو الجزء الذي يدعو المشاهد لاتخاذ إجراء محدد بعد مشاهدة الفيديو أو خلاله. الهدف هو دفع المشاهد للقيام بشيء معين
  
  
class ServiceVideo(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="videos")  # ربط الفيديو بالخدمة

    video_file = models.FileField(upload_to='service_videos/', blank=True, null=True, help_text="Upload a video for this service")
    description = models.TextField(blank=True, help_text="Optional description for the video")  # وصف اختياري للفيديو
    uploaded_at = models.DateTimeField(auto_now_add=True)  # تاريخ ووقت رفع الفيديو

    class Meta:
        indexes = [
            models.Index(fields=['service']),  # فهرس على الحقل service
        ]

    def __str__(self):
        return f"Video for {self.service.service_name} ({self.service.creator})"
    

class Category(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name



class Content(models.Model):
    REVIEWS = "R"
    UNBOXING_PRODUCTS = "U"
    TUTORIALS = "T"
    GIVEAWAY_DISCOUNTS = "G"

    UGC_TYPE_CHOICES = [(REVIEWS, "Reviews & Testimonials"), 
                      (UNBOXING_PRODUCTS, "Unboxing products"),
                      (TUTORIALS, "Tutoials & How to use"),
                      (GIVEAWAY_DISCOUNTS, "Giveaway & Discounts")]
    PLATFORM_CHOICES = [
        ('Instagram', 'Instagram'),
        ('Facebook', 'Facebook'),
        ('Snapchat', 'Snapchat'),
        ('Tiktok', 'Tiktok'),
        ('Youtube', 'Youtube'),
    ]

    id = models.UUIDField(default=uuid4, primary_key=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="contents")
    category = models.ManyToManyField(Category, related_name="content")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="contents", help_text="Service associated with this content", default='1')  # ربط المحتوى بخدمة معينة
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='Instagram')
    title = models.CharField(max_length=255)
    description = models.TextField()
    ugc_type = models.CharField(max_length=1, choices=UGC_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    is_portfolio_item = models.BooleanField(default=True)  # هل هذا المحتوى ضمن Portfolio



    class Meta:
        ordering = ["ugc_type", "views_count"]
        indexes = [
            models.Index(fields=['service', 'ugc_type', 'platform'])
        ]

    def __str__(self):
        return self.title
    

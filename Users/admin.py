from django.contrib import admin
from django.db.models import Count, F
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, 
    Brand, 
    Creator, 
    )


# class UserAdmin(admin.ModelAdmin):
#     list_display = ['username', 'email', 'user_type', 'gender', 'creator', 'brand']
#     list_filter = ['user_type', 'gender']
#     list_per_page = 10
#     ordering = ['username']
#     search_fields = ['username', 'email']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # لعرض الحقول المخصصة في قائمة المستخدمين
    list_display = ['username', 'email', 'user_type', 'gender', 'creator', 'brand']
    # لتصفية المستخدمين بناءً على نوع المستخدم والجنس
    list_filter = ['user_type', 'gender', 'is_active', 'is_staff']
    # لتحديد عدد المستخدمين المعروضين في كل صفحة
    list_per_page = 10
    # للبحث عن المستخدمين بناءً على هذه الحقول
    search_fields = ['username', 'email']
    # لترتيب المستخدمين بناءً على اسم المستخدم
    ordering = ['username']

    # لتخصيص الحقول المعروضة عند عرض تفاصيل مستخدم معين
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_date",
                    "gender",
                    "country",
                    "email",
                    "user_type",  # إضافة user_type
                )
            },
        ),
        
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # تخصيص الحقول عند إنشاء مستخدم جديد
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_date",
                    "gender",
                    "country",
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "user_type",  # إضافة user_type عند إنشاء مستخدم
                ),
            },
        ),
    )

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['user', 'about_me', 'order_number', 'avg_order_time', 'avg_response_speed', 'last_seen', 'register_date']
    list_filter = ['register_date', 'last_seen']
    list_per_page = 10
    ordering = ['register_date']

@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'clients_number', 'services_number', 'last_seen']
    list_filter = ['register_date', 'last_seen']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    list_per_page = 10
    
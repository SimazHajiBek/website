from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Users'

    def ready(self):
        # استدعاء ملف signals عند تشغيل التطبيق
        import Users.signals

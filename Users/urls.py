from django.urls import path, include
from django.urls import re_path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.routers import DefaultRouter
from .views import  UserViewSet, CreatorViewSet, BrandViewSet, get_followers_view


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'creators', CreatorViewSet, basename='creators')


urlpatterns = [
    path('', include(router.urls)),
    path('get_followers/', get_followers_view, name='get_followers'),  # ✅ تسجيل الـ View Function العادي

    
]

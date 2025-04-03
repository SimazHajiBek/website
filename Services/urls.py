from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet, 
    ServiceVideoViewSet,
    # RecentlyAddedContentView,
    # PlatformContentView,
    CategoryViewSet,
    ContentViewSet,
    )

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-videos', ServiceVideoViewSet, basename='service-video')
# router.register(r'recently-added', RecentlyAddedContentView, basename='recently-added')
# router.register(r'platform', PlatformContentView, basename='platform-content')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'contents', ContentViewSet, basename='contents')

urlpatterns = [
    path('', include(router.urls)),
]

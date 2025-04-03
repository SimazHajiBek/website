# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ChatViewSet, MessageViewSet

# router = DefaultRouter()
# router.register('chats', ChatViewSet)
# router.register('messages', MessageViewSet, basename='messages')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]

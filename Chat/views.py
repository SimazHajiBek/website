# from rest_framework.viewsets import ModelViewSet
# from rest_framework.filters import SearchFilter
# from .models import Chat, Message
# from .serializers import ChatSerializer, MessageSerializer

# class ChatViewSet(ModelViewSet):
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer

#     def get_queryset(self):
#         """
#         فلترة الدردشة حسب brand_id أو creator_id
#         """
#         queryset = Chat.objects.all()
#         brand_id = self.request.query_params.get('brand_id')
#         creator_id = self.request.query_params.get('creator_id')

#         if brand_id:
#             queryset = queryset.filter(brand_id=brand_id)
#         if creator_id:
#             queryset = queryset.filter(creator_id=creator_id)

#         return queryset

# class MessageViewSet(ModelViewSet):
#     #queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['message']  # تحديد الحقول التي يمكن البحث فيها

    
#     def get_queryset(self):
#         """
#         إرجاع الرسائل التي تعود إلى مرسل معين إذا كان هناك فلتر.
#         """
#         sender_id = self.request.query_params.get('sender_id')
#         if sender_id:
#             return Message.objects.filter(sender_id=sender_id)
#         return Message.objects.all()
    




from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

class ChatViewSet(ModelViewSet):
    """
    ViewSet للدردشات، مع دعم الفلترة حسب `brand_id` أو `creator_id`.
    """
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['brand_id', 'creator_id']  # دعم الفلترة المباشرة بدون تعريف `get_queryset`.

    def get_queryset(self):
        """
        فلترة إضافية عند الحاجة.
        """
        queryset = super().get_queryset()
        # يمكنك إضافة منطق إضافي هنا إذا تطلب الأمر.
        return queryset


class MessageViewSet(ModelViewSet):
    """
    ViewSet للرسائل مع دعم البحث حسب النص والفلترة حسب `sender_id`.
    """
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['message']  # البحث داخل نص الرسالة.
    filterset_fields = ['sender_id']  # فلترة مباشرة بدون الحاجة لكتابة فلتر يدوي.

    def get_queryset(self):
        """
        استدعاء قاعدة البيانات فقط إذا كان هناك شرط إضافي.
        """
        queryset = super().get_queryset()
        # إضافة أي معالجة إضافية هنا إذا لزم الأمر.
        return queryset

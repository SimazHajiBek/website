from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend  # استيراد DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Service, ServiceVideo, Content, Category
from .serializers import (
    ServiceSerializer, 
    ServiceVideoSerializer, 
    ContentSerializer, 
    CategorySerializer,
    PortfolioContentSerializer
    )
from .pagination  import DefaultPagination


class ServiceViewSet(ModelViewSet):
    """
    إدارة الخدمات:
    - أي شخص يمكنه مشاهدة الخدمات.
    - فقط الـ Creator يمكنهم إنشاء، تعديل، وحذف الخدمات الخاصة بهم.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]  
    filterset_fields = ['platform']  
    pagination_class = DefaultPagination

    def get_permissions(self):
        """
        - السماح للجميع بمشاهدة الخدمات.
        - السماح فقط لـ Creator بالتحكم بالخدمات.
        """
        #if self.action in ["list", "retrieve"]:
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        عرض جميع الخدمات للجميع، ولكن عند التعديل أو الحذف يجب أن يكون المستخدم هو الـ Creator.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return Service.objects.filter(creator=self.request.user.creator)
        return Service.objects.all()

    def perform_create(self, serializer):
        """
        عند إنشاء خدمة جديدة، يتم ربطها تلقائيًا بـ Creator المسجل.
        """
        user = self.request.user
        if not hasattr(user, 'creator'):
            raise PermissionDenied("فقط منشئو المحتوى (Creator) يمكنهم إضافة خدمات.")
        serializer.save(creator=user.creator)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_video(self, request, pk=None):
        """
        السماح فقط لـ Creator بإضافة فيديو لخدماتهم الخاصة.
        """
        service = self.get_object()
        if service.creator != request.user.creator:
            raise PermissionDenied("لا يمكنك إضافة فيديو لخدمة لا تملكها.")

        serializer = ServiceVideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(service=service)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ServiceVideoViewSet(ModelViewSet):
    """
    إدارة فيديوهات الخدمات:
    - أي شخص يمكنه مشاهدة الفيديوهات.
    - فقط الـ Creator يمكنهم إنشاء، تعديل، وحذف الفيديوهات الخاصة بهم.
    """
    queryset = ServiceVideo.objects.all()
    serializer_class = ServiceVideoSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        """
        - السماح للجميع بمشاهدة الفيديوهات.
        - السماح فقط لـ Creator بالتحكم بها.
        """
        #if self.action in ["list", "retrieve"]:
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        - عرض جميع الفيديوهات للجميع.
        - السماح فقط لـ Creator بالتحكم بالفيديوهات الخاصة بخدماتهم.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return ServiceVideo.objects.filter(service__creator=self.request.user.creator)
        return ServiceVideo.objects.all()

    def perform_create(self, serializer):
        """
        - السماح فقط لـ Creator بإضافة فيديوهات للخدمات الخاصة بهم.
        """
        user = self.request.user
        if not hasattr(user, 'creator'):
            raise PermissionDenied("فقط منشئو المحتوى (Creator) يمكنهم إضافة فيديوهات.")

        service = serializer.validated_data.get("service")
        if service.creator != user.creator:
            raise PermissionDenied("لا يمكنك إضافة فيديو لخدمة لا تملكها.")

        serializer.save()


# عرض الفئات
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ContentViewSet(ReadOnlyModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination

    # دعم الفلاتر
    filterset_fields = {
        'platform': ['exact'],         # تصفية بناءً على المنصة
        'ugc_type': ['exact'],         # تصفية بناءً على نوع المحتوى
        'creator__user__gender': ['exact'],  # تصفية المحتوى بناءً على جنس المستخدم
        'service__voice_over': ['exact'],  # تصفية حسب Voice Over
        'service__face_appearing': ['exact'],  # تصفية حسب Face Appearing
        #'rank': ['gte', 'lte'],        # تصفية بناءً على التقييم (>= أو <=)
        'category': ['exact'],         # تصفية بناءً على الفئة
    }
     # عرض المحتوى حسب المنصة
    @action(detail=False, methods=['get'], url_path='platform/(?P<platform>[^/.]+)')
    def by_platform(self, request, platform=None):
        # platform_contents = self.queryset.filter(platform=platform)
        # serializer = self.get_serializer(platform_contents, many=True)
        # return Response(serializer.data)

        queryset = self.filter_queryset(self.get_queryset().filter(platform=platform))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # عرض المحتوى المضاف حديثًا
    @action(detail=False, methods=['get'], url_path='recently-added')
    def recently_added(self, request):
        # recent_contents = self.queryset.order_by('-uploaded_at')[:10]
        # serializer = self.get_serializer(recent_contents, many=True)
        # return Response(serializer.data)
        queryset = self.filter_queryset(self.get_queryset().order_by('-uploaded_at')[:10])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='portfolio/(?P<creator_id>[^/.]+)')
    def portfolio(self, request, creator_id=None):
        queryset = self.get_queryset().filter(creator_id=creator_id, is_portfolio_item=True)
        serializer = PortfolioContentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-to-portfolio')
    def add_to_portfolio(self, request, pk=None):
        content = self.get_object()
        content.is_portfolio_item = True
        content.save()
        serializer = PortfolioContentSerializer(content)  # إعادة البيانات باستخدام Serializer
        return Response(serializer.data, status=201)     

    @action(detail=True, methods=['post'], url_path='remove-from-portfolio')
    def remove_from_portfolio(self, request, pk=None):
        content = self.get_object()
        content.is_portfolio_item = False # إزالة العنصر من البورتفوليو
        content.save()
        return Response({'message': 'Content removed from portfolio successfully!'}, status=200)

    
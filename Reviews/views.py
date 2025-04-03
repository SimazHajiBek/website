from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
    
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from Orders.models import OrderItem
from .models import Review
from .serializers import ReviewSerializer
from .pagination  import DefaultPagination

class ReviewViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    serializer_class = ReviewSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        """
        - السماح لأي شخص بمشاهدة التقييمات.
        - السماح فقط للمستخدمين المسجلين بحذف أو تعديل أو إضافة التقييمات.
        """
        #if self.action in ["list", "retrieve"]:
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        - عرض جميع التقييمات الخاصة بـ Creator معين.
        - إذا لم يتم تمرير `creator_id` في الرابط، يتم عرض جميع التقييمات.
        """
        creator_id = self.kwargs.get('creator_id')  # الحصول على معرف الـ Creator من الرابط
        if creator_id:
            return Review.objects.filter(creator_id=creator_id)  # جلب التقييمات الخاصة بـ Creator معين
        return Review.objects.all()

    def perform_create(self, serializer):
        """
        - السماح فقط للعلامات التجارية (Brand) بإضافة تقييمات.
        """
        # user = self.request.user
        # if not hasattr(user, 'brand'):
        #     raise PermissionDenied("فقط العلامات التجارية (Brand) يمكنهم إضافة تقييمات.")

        # serializer.save(brand=user.brand)  # تعيين الـ Brand تلقائيًا
        ###
        user = self.request.user
        if not hasattr(user, 'brand'):
            raise PermissionDenied("Only brands can add reviews.")

        service_id = self.request.data.get('service')  
        creator_id = self.request.data.get('creator')  
        # التحقق مما إذا كان الـ Brand قد اشترى هذه الخدمة من هذا الـ Creator
        has_purchased = OrderItem.objects.filter(
            order__brand=user.brand,
            service_id=service_id,
            service__creator_id=creator_id
        ).exists()

        if not has_purchased:
            raise PermissionDenied("You cannot rate this service because it was not purchased from this Creator.")

        serializer.save(brand=user.brand)  



    def perform_destroy(self, instance):
        """
        - السماح فقط للعلامة التجارية (Brand) التي أنشأت التقييم بحذفه.
        """
        user = self.request.user
        if user.brand != instance.brand:
            raise PermissionDenied("You cannot delete this rating.")
        instance.delete()

    def perform_update(self, serializer):
        """
        - السماح فقط للعلامة التجارية (Brand) التي أنشأت التقييم بتعديله.
        """
        user = self.request.user
        review = self.get_object()
        if user.brand != review.brand:
            raise PermissionDenied("You cannot edit this rating.")
        serializer.save()

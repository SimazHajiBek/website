from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework import status
from Services.models import Service
from Users.models import Creator
from .models import Order, Payment, Cart, CartItem, Withdrawal, OrderItem, Balance, Transaction
from .serializers import(
    OrderSerializer, 
    # DetailedOrderSerializer,
    PaymentSerializer, 
    #CartItemSerializer, 
    CartSerializer, 
    WithdrawalSerializer,
    OrderItemSerializer,
    CreateOrderSerializer,
    UpdateOrderItemSerializer,
    UpdateOrderSerializer,
    CartItemSerializer,
    UpdateCartItemSerializer,
    IncomingOrderSerializer,
    BalanceSerializer,
    TransactionSerializer,
    PurchaseSerializer
)
from .pagination  import DefaultPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)

class IncomingRequestsViewSet(ReadOnlyModelViewSet):
    """ استعراض الطلبات الواردة للـ Creator """
    serializer_class = IncomingOrderSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # دعم الفلاتر
    filterset_fields = {
        'status': ['exact'],         
    }


    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "creator"):
            return Order.objects.none()# إرجاع قائمة فارغة إذا لم يكن المستخدم Creator

        # 🔹 إنشاء مفتاح Cache فريد لكل مستخدم
        cache_key = f"incoming_orders_{user.id}"
        cached_queryset = cache.get(cache_key)

        if cached_queryset:
            print("✅ استرجاع البيانات من الكاش!")
            return cached_queryset  # إرجاع البيانات من الكاش إذا كانت متاحة

        queryset = Order.objects.filter(creator=user.creator)

        # ✅ فلترة الطلبات حسب الحالة (status)
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset
    # ✅ تطبيق `cache_page` على `list` لتحسين الأداء
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CartItemViewSet(ModelViewSet):
    #serializer_class = CartItemSerializer
    pagination_class = DefaultPagination


    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        # جلب عناصر العربة الخاصة بالمستخدم
        cart = Cart.objects.get(brand=self.request.user.brand)
        return CartItem.objects.filter(cart=cart).select_related('service')

    def get_serializer_context(self):
        # تمرير العربة الحالية إلى السيريالايزر
        context = super().get_serializer_context()
        context['cart'], _ = Cart.objects.get_or_create(brand=self.request.user.brand)
        return context

    @action(detail=False, methods=['post'], url_path='add')
    def add_to_cart(self, request):
        """
        إضافة عنصر إلى العربة أو تحديث الكمية إذا كان موجودًا.
        """
        user = request.user
        cart, _ = Cart.objects.get_or_create(brand=self.request.user.brand)
        service_id = request.data.get('service')
        quantity = int(request.data.get('quantity', 1))

         # تحقق إذا كان service_id قاموسًا واستخرج المعرف إذا كان كذلك
        if isinstance(service_id, dict):
            service_id = service_id.get('id')


        # التأكد من وجود العنصر في العربة أو إنشائه
        #cart_item, created = CartItem.objects.get_or_create(cart=cart, service_id=service_id)
        
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

    # التأكد من وجود العنصر أو تحديث كميته
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, service=service,
            defaults={'quantity': quantity, 'price': service.price}
        )

        if not created:
            cart_item.quantity += int(quantity)  # تحديث الكمية
            cart_item.save()

        # 🛑 مسح الكاش بعد تحديث البيانات
        cache_key = f"cart_items_{user.id}"
        cache.delete(cache_key)

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=True, methods=['delete'], url_path='remove')
    # def remove_from_cart(self, request, pk=None):
    #     """
    #     حذف عنصر معين من العربة.
    #     """
    #     item = self.get_object()
    #     item.delete()
    #     return Response({"detail": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)

#هذا ال View يحتاج الى ادراج pk بسبب وجود RetrieveModelMixin وها شيء غير ضروري هنا
# class CartViewSet(RetrieveModelMixin, GenericViewSet):

class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        """
        - جلب العربة الخاصة بالمستخدم إذا كانت موجودة.
        """
        return Cart.objects.prefetch_related('items__service').filter(brand=self.request.user.brand)

    def create(self, request, *args, **kwargs):
        """
        - السماح فقط للمستخدمين الذين لديهم `Brand` بإنشاء عربة.
        - لا حاجة لإرسال `brand_id` يدويًا، سيتم ربط العربة بالمستخدم تلقائيًا.
        """
        user = request.user

        # التحقق مما إذا كان المستخدم يملك `Brand`
        if not hasattr(user, 'brand'):
            return Response({"error": "يجب أن تكون لديك علامة تجارية (Brand) لإنشاء عربة."}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء العربة فقط إذا لم تكن موجودة
        cart, created = Cart.objects.get_or_create(brand=user.brand)

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """
        مسح جميع العناصر من العربة.
        """
        cart, _ = Cart.objects.get_or_create(brand=request.user.brand)
        cart.items.all().delete()
        return Response({"detail": "Cart has been cleared."}, status=status.HTTP_204_NO_CONTENT)
    

class OrderViewSet(ModelViewSet):
    #serializer_class = OrderSerializer
    http_method_names = ['post', 'get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data = request.data,
            context = {'brand_id' : self.request.user.brand.id}
            )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method =='PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(brand=self.request.user.brand).order_by('-created_at')

class OrderItemViewSet(ModelViewSet):
    http_method_names = ['patch', 'delete', 'get']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateOrderItemSerializer  # ✅ السماح بتعديل الكمية فقط
        return OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(order__brand=self.request.user.brand)


class PurchaseViewSet(ReadOnlyModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # دعم الفلاتر
    filterset_fields = {
        'order__status': ['exact'],         
    }


    def get_queryset(self):
        user = self.request.user
        
        # التأكد من أن المستخدم لديه براند
        if not hasattr(user, "brand"):
            return OrderItem.objects.none()
    
        # جلب الطلبات التي قام بها البراند والتي تخص Creator معين
        queryset = OrderItem.objects.filter(
            order__brand=user.brand  # الفلترة بناءً على البراند الذي قام بالشراء
        )

        # تصفية الطلبات بناءً على الحالة (اختياري)
        status = self.request.query_params.get("status")
        if status in ['in_progress', 'delivered', 'canceled']:
            queryset = queryset.filter(status=status)

        return queryset


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    print(Payment.objects.filter(payment_status='SUCCESS'))

    def get_queryset(self):
        """إرجاع المدفوعات بناءً على المستخدم (Brand)"""
        return Payment.objects.filter(brand=self.request.user.brand).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_payment(self, request, pk=None):
        """إلغاء الدفع قبل تحويل الأموال"""
        try:
            payment = self.get_object()
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        if payment.payment_status != 'PENDING':
            return Response({"error": "Cannot cancel a processed payment."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ إرجاع الأموال للـ Brand
        refund_money_to_brand(payment)

            # ✅ تحديث حالة الدفع
        payment.payment_status = 'CANCELED'
        payment.save()

        return Response({"message": "Payment canceled successfully."}, status=status.HTTP_200_OK)

    def refund_money_to_brand(payment):
        """محاكاة إرجاع الأموال إلى Brand (يتم استبدالها بخدمة دفع حقيقية)"""
        print(f"🚫 تم إرجاع {payment.amount} إلى {payment.brand.user.email}")


class BalanceHistoryViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Creator.objects.all()
    lookup_field = 'id'  # لتحديد البحث عن طريق الـ id

    def retrieve(self, request, *args, **kwargs):
        try:
            creator = self.get_object()  # الحصول على الكائن باستخدام GenericViewSet

            # الحصول على بيانات الرصيد
            balance = Balance.objects.get(creator=creator)
            balance_data = BalanceSerializer(balance).data

            # طلب السحب الأخير
            latest_withdrawal = Withdrawal.objects.filter(creator=creator, state='in_progress').last()
            withdrawal_data = WithdrawalSerializer(latest_withdrawal).data if latest_withdrawal else None

            # استرجاع المعاملات
            transactions = Transaction.objects.filter(creator=creator).order_by('-date')
            transactions_data = TransactionSerializer(transactions, many=True).data

            return Response({
                'balance': balance_data,
                'withdrawal_request': withdrawal_data,
                'history': transactions_data,
            })

        except Creator.DoesNotExist:
            return Response({"error": "Creator not found"}, status=404)

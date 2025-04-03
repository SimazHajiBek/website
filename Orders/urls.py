from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CartItemViewSet,
    CartViewSet,
    IncomingRequestsViewSet,
    BalanceHistoryViewSet,
    PurchaseViewSet,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    
)

# إنشاء DefaultRouter
router = DefaultRouter()

# تسجيل ViewSets مع الـ Router
# router.register(r'orders', OrderViewSet, basename="orders")
# router.register(r'order-items', OrderItemViewSet, basename="order-items")
#OrderViewSet لإدارة الطلبات بشكل عام، ويشمل داخله OrderItems لكنه لا يعالجها بشكل منفصل.
#OrderItemViewSet للتعامل المباشر مع العناصر داخل الطلبات، مثل إضافة عنصر، حذفه، أو استعراض عناصر الطلبات فقط.

router.register(r'purchases', PurchaseViewSet, basename="purchases")
router.register(r"incoming-requests", IncomingRequestsViewSet, basename="incoming-requests")

router.register(r'payments', PaymentViewSet, basename='payment')

router.register(r'cart/items', CartItemViewSet, basename='cart-item')
router.register(r'cart', CartViewSet, basename='cart')

router.register('creator/balance-history', BalanceHistoryViewSet, basename='creator-balance-history')

router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-items')



# تضمين المسارات في urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # تضمين جميع المسارات من الـ Router
]

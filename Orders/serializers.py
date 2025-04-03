from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from Users.models import Brand
from .models import Order, Payment, Withdrawal, Cart, CartItem, OrderItem, Balance, Transaction
from Users.serializers import BrandSerializer, CreatorSerializer

# لIncoming Requests التي تخص البائع وهو ال creator
class OrderItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.service_name")  # إظهار اسم الخدمة بدلاً من الـ ID

    class Meta:
        model = OrderItem
        fields = ["id", "service", "service_name", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    fee = serializers.StringRelatedField()
    promo_code = serializers.StringRelatedField()
    class Meta:
        model = Order
        fields = ['items', 'total_price', 'fee', 'promo_code', 'total_cost']
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk = cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id = cart_id).count == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            brand = Brand.objects.get(id=self.context['brand_id'])
            cart = Cart.objects.get(pk=cart_id)  # ✅ جلب العربة للحصول على الرسوم وكود الخصم
            
            order = Order.objects.create(
                brand=brand,
                creator=brand.creator if hasattr(brand, 'creator') else None,  # ✅ إضافة المنشئ إذا وُجد
                fee=cart.fee,  # ✅ إضافة الرسوم
                promo_code=cart.promo_code  # ✅ إضافة كود الخصم
            )

            cart_items = CartItem.objects.select_related('service').filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    service=item.service,
                    price=item.price,
                    quantity=item.quantity,
                    profit=item.price * item.quantity * Decimal(0.8)   # ✅ إضافة حساب الربح
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # ✅ تصفير العربة بدلاً من حذفها نهائياً
            cart.items.all().delete()
            cart.promo_code = None
            cart.fee = None
            cart.save()

            return order
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]  # ✅ السماح بتحديث الحالة فقط



class UpdateOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["quantity"]  # ✅ السماح بتحديث الكمية فقط

        
class IncomingOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    brand_name = serializers.CharField(source="brand.brand_name")  # عرض اسم البراند
    total_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()  # ✅ إضافة الأرباح

    class Meta:
        model = Order
        fields = ["id", "brand_name", "status", "created_at", "items", "total_price", "total_profit"]

    def get_total_price(self, obj):
        return obj.total_price()
    
    def get_total_profit(self, obj):
        return obj.total_profit()

class PaymentSerializer(serializers.ModelSerializer):
    payment_status = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='order.total_price', read_only=True)
    fee = serializers.SerializerMethodField()        # قيمة الرسوم
    total_cost = serializers.SerializerMethodField() # السعر الكلي
 
    class Meta:
        model = Payment
        fields = [
            'price', 
            'fee', 
            'total_cost', 
            'payment_method', 
            'payment_status',
            'card_holder_name',
            'card_number',
            'card_expiry',
            'card_cvc'
            ]

    def get_fee(self, obj):
        # الحصول على قيمة الرسوم من order
        return obj.order.fee.amount if obj.order.fee else 0

    def get_total_cost(self, obj):
        # حساب السعر الكلي من order
        return obj.order.total_cost()
    
    def get_fee(self, obj):
        """إرجاع قيمة الرسوم إذا كانت موجودة، وإلا يتم إرجاع 0"""
        return obj.order.fee.amount if hasattr(obj.order, 'fee') and obj.order.fee else 0

    def validate_payment_method(self, value):
        """التحقق من أن طريقة الدفع صحيحة"""
        if value not in dict(Payment.PAYMENT_CHOICES).keys():
            raise serializers.ValidationError("طريقة الدفع غير صحيحة.")
        return value

    def create(self, validated_data):
        """تحديث حالة الدفع إلى 'SUCCESS' تلقائيًا عند إنشائه"""
        validated_data['payment_status'] = 'SUCCESS'
        return super().create(validated_data)

class WithdrawalSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = Withdrawal
        fields = ['creator', 'amount', 'withdrawal_method', 'account_details', 'state', 'created_at']
        read_only_fields = ['created_at']


# 🛒 Serializer لعناصر العربة
class CartItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.service_name",  read_only=True)
    video_length = serializers.IntegerField(source="service.video_length", read_only=True)
    hooks_numbers = serializers.IntegerField(source="service.hooks_numbers", read_only=True)
    call_to_action = serializers.IntegerField(source="service.call_to_action_number", read_only=True)
    face_appearing = serializers.BooleanField(source="service.face_appearing", read_only=True)
    voice_over = serializers.BooleanField(source="service.voice_over", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "service", "service_name", "video_length", "hooks_numbers", "call_to_action",
            "face_appearing", "voice_over", "quantity", "price", "total_price"
        ]
        read_only_fields = ["price", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price()

    def create(self, validated_data):
        # عند إضافة عنصر للعربة، نتحقق من وجوده مسبقًا
        cart = self.context['cart']
        service = validated_data['service']
        quantity = validated_data['quantity']

         # تعيين price تلقائيًا بناءً على service.price
        price = service.price


        item, created = CartItem.objects.get_or_create(
            cart=cart,
            service=service,
            defaults={'quantity': quantity, 'price': price }
        )

        if not created:
            # إذا كان العنصر موجودًا بالفعل، نقوم بتحديث الكمية
            item.quantity += quantity
            item.save()

        return item

    def update(self, instance, validated_data):
        # تعديل الكمية فقط عند التحديث
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]

# 🛒 Serializer للعربة (تحتوي على عناصر العربة)
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    # fee = serializers.SerializerMethodField()
    # promo_code = serializers.SerializerMethodField()
    # total_cost = serializers.SerializerMethodField()

   # brand = serializers.StringRelatedField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_items"]#, "fee", "promo_code", "total_cost" ]

    def get_total_price(self, obj):
        return obj.total_price()

    def get_total_items(self, obj):
        return obj.total_items()
    
    def get_fee(self, obj):
        return Order.fee
    
    def get_promo_code(self, obj):
        return Order.promo_code
    
    def get_total_cost(self, obj):
        return Order.total_cost(self)
    


class PurchaseSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.service_name")
    creator = serializers.CharField(source="order.creator.user.username")
    status = serializers.CharField(source="order.status")
    created_at = serializers.DateTimeField(source="order.created_at")
    total_profit = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["total_profit", "status", "creator", "service_name", "created_at"]

    def get_total_profit(self, obj):
        return obj.price * obj.quantity# * 0.8# الارباح هي 80 بالمية


class BalanceSerializer(serializers.ModelSerializer):
    total_balance = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = ['withdrawable_balance', 'pending_balance', 'total_balance']

    def get_total_balance(self, obj):
        return obj.total_balance# ✅ صحيح: الوصول إلى الخاصية بدون أقواس.

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'withdrawal_method', 'account_details', 'date', 'state']

# class HistorySerializer(serializers.Serializer):
#     id = serializers.CharField()
#     service = serializers.CharField()
#     date = serializers.DateField()
#     amount = serializers.DecimalField(max_digits=12, decimal_places=2)
#     balance_after = serializers.DecimalField(max_digits=12, decimal_places=2)
#     transaction_type = serializers.CharField()

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'service', 'date', 'current_balance', 'id']
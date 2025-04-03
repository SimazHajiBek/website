
from typing import Any
from django.db.models import Count, F
from django.contrib import admin
from django.urls import reverse
from django.db.models.functions import Coalesce
from django.utils.html import format_html
from django.utils.http import urlencode
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Order, Payment, Withdrawal, Cart, CartItem, OrderItem, PromoCode, Fee, Balance, Transaction


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_amount', 'is_active']
    list_filter = ['is_active']
    ordering = ['is_active', 'code']
    list_per_page = 10

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount']
    list_per_page = 10
    ordering = ['name']


class OrderItemInLine(admin.TabularInline):
    extra = 0
    autocomplete_fields = ['service']
    
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    list_display = [
        'brand', 
        'creator', 
        'total_price', 
        'status', 
        'created_at', 
        'promo_code', 
        'fee', 
        'payments',
        'items_count']
    list_filter = ['status', 'created_at','brand']
    inlines = [OrderItemInLine]
    search_fields = ['brand__brand_name__istartswith']
    list_per_page = 10
    ordering = ['status']

    @admin.display(ordering="payments")
    def payments(self, obj):
        url = (
            reverse("admin:Orders_payment_changelist")
            + "?"
            + urlencode({"order_id": str(obj.id)})
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.payments} payments",
        )

    @admin.display(ordering="items_count")
    def items_count(self, obj):
        url = (
            reverse("admin:Orders_orderitem_changelist")
            + "?"
            + urlencode({"order_id": str(obj.id)})
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.items_count} items",
        )
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            payments=Coalesce(Count(F("payment"), distinct=True), 0), 
            items_count=Coalesce(Count(F("items"), distinct=True), 0),            
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'service', 'quantity', 'price']
    list_filter = ['service', 'order']
    list_per_page = 10
    ordering = ['price']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'order', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'created_at']
    list_select_related = ["brand"]
    search_fields = ['brand__brand_name']
    ordering = ['payment_status']

    # def has_add_permission(self, request: HttpRequest) -> bool:
    #     return False

    # def has_change_permission(
    #     self, request: HttpRequest, obj: Any | None = ...
    # ) -> bool:
    #     return False

    # def has_delete_permission(
    #     self, request: HttpRequest, obj: Any | None = ...
    # ) -> bool:
    #     return False



@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'creator', 'amount', 'withdrawal_method', 'state']
    list_filter = ['state', 'withdrawal_method']
    list_select_related = ["creator"]
    ordering = ['withdrawal_method']


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['creator', 'withdrawable_balance', 'pending_balance']
    list_select_related = ["creator"]
    search_fields = ['creator__user__username']
    list_per_page = 10
    ordering = ['withdrawable_balance']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['creator', 'amount', 'transaction_type', 'date', 'service', 'current_balance']
    list_filter = ['transaction_type', 'service']
    list_select_related = ["creator"]
    search_fields = ['creator__user__username', 'transaction_type']
    list_per_page = 10
    ordering = ['transaction_type']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'created_at', 'updated_at', 'items_count']
    list_filter = ['brand']
    list_select_related = ["brand"]
    search_fields = ['brand__brand_name']

    
    @admin.display(ordering="items_count")
    def items_count(self, obj):
        url = (
            reverse("admin:Orders_cartitem_changelist")
            + "?"
            + urlencode({"cart__id": str(obj.id)})
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.items_count} items_count",
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(items_count=Count("items"))


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'service', 'quantity']
    list_filter = ['service','cart']
    list_select_related = ["service"]
    search_fields = ['service__service_name']
    ordering = ['service', 'quantity']




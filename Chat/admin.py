from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.db.models import Count, F
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['brand', 'creator', 'created_at', 'messages_count']
    list_per_page = 10
    ordering = ['created_at']

    @admin.display(ordering='messages_count')
    def messages_count(self, obj):
        url =(
            reverse("admin:Chat_message_changelist")
            +'?'
            +urlencode({'chat_id': str(obj.id)})
        )

        return format_html(
            '<a href="{}"> {} </a>',
            url,
            f"{obj.messages_count} Messages"
        )
    
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(messages_count = Count("messages"))
        )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_id', 'message', 'created_at']
    list_filter = ['created_at',]
    list_per_page = 10
    ordering = ['created_at']
    search_fields = ['sender__username', 'message']

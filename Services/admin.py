from django.contrib import admin
from django.db.models import Count, F
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from .models import Service, ServiceVideo, Category, Content


class ServiceVideoInline(admin.TabularInline):
    model = ServiceVideo
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'service_name',
        'platform',
        'video_length',
        'hooks_numbers',
        'call_to_action_number',
        'voice_over',
        'face_appearing',
        'price',
        'created_at',
        'updated_at',
        'videos_number'
    ]
    list_filter = ['platform']
    search_fields = ['service_name__istartswith']
    list_per_page = 10
    inlines = [ServiceVideoInline]


    
    @admin.display(ordering='videos_number')
    def videos_number(self, obj):
        url = (             
            reverse("admin:Services_servicevideo_changelist")
            +'?'
            + urlencode({'service__id': str(obj.id)})
        )

        return  format_html(
            '<a href="{}"> {} </a>',
            url,
            f"{obj.videos_number} services"
        )
    
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(videos_number = Count("videos"))
        )



@admin.register(ServiceVideo)
class ServiceVideoAdmin(admin.ModelAdmin):
    list_display = [
        'service',
        'video_file',
        'description',
        'uploaded_at'
    ]
    list_filter = ['service']
    list_per_page = 10



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'created_at',
        'updated_at',
        'content_number'
    ]
    list_per_page = 10


    
    @admin.display(ordering='content_number')
    def content_number(self, obj):
        url = (             
            reverse("admin:Services_content_changelist")
            +'?'
            + urlencode({'category__id': str(obj.id)})
        )

        return  format_html(
            '<a href="{}"> {} </a>',
            url,
            f"{obj.content_number} categories"
        )
    
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(content_number = Count("content"))
        )



@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'service',
        'platform',
        #'category',
        'title',
        'description',
        'ugc_type',
        'uploaded_at',
        'views_count',
        
    ]
    list_filter = ['platform','ugc_type']
    list_select_related = ['category']
    ordering = ['ugc_type']
    list_per_page = 10

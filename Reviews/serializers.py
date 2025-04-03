from rest_framework import serializers
from django.db.models import Avg
from Users.models import Creator
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    brand_name = serializers.StringRelatedField(source='brand')  # لعرض اسم العلامة التجارية
    service_video_name = serializers.StringRelatedField(source='service_video')  # اسم الفيديو

    class Meta:
        model = Review
        fields = [
            'creator', 
            'brand_name', 
            'rating', 
            'review', 
            'service_video_name', 
            'created_at']


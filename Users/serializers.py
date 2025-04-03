from rest_framework import serializers
from django.db.models import Avg
from Reviews.serializers import ReviewSerializer
from .models import (
    User, 
    Brand, 
    Creator, 
   )

class UserSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "gender",
            "country",
            "email",  # يمكنك إضافة المزيد من الحقول حسب حاجتك.
        ]
    def get_country(self, obj):
        return obj.country.name if obj.country else None


# Serializer لعرض بيانات Brand
class BrandSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # يمكن تعديلها إذا أردت تحديث بيانات المستخدم

    class Meta:
        model = Brand
        fields = [
            'user',
            'about_me',
            'facebook_followers',
            'instagram_followers',
            'youtube_followers',
            'tiktok_followers',
            'snapchat_followers',
            'order_number',
            'avg_order_time',
            'avg_response_speed',
            'last_seen',
            'register_date'
        ]
        read_only_fields = ['order_number', 'avg_order_time', 'avg_response_speed', 'last_seen']  # جعل الحقول التي يتم تحديثها تلقائيًا للقراءة فقط.


# Serializer لتسجيل حساب جديد كـ Brand
class BrandSignUpSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(max_length=255)
    country = serializers.CharField(source='user.country', read_only=True)  # عرض اسم البلد فقط
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()

    class Meta:
        model = Brand
        fields = ['email', 'password', 'confirm_password', 'brand_name', 'phone_number', 'country']

    def validate(self, data):
        """
        التحقق من أن كلمة المرور وتأكيد كلمة المرور متطابقان.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """
        إنشاء حساب جديد وربط المستخدم بـ Brand.
        """
        email = validated_data.pop('email')
        phone_number = validated_data.pop('phone_number')
        country = validated_data.pop('country')
        password = validated_data.pop('password')
        brand_name = validated_data.pop('brand_name')


        # إنشاء المستخدم
        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password, 
        )
        user.country = country
        user.phone_number = phone_number
        user.save()

        # إنشاء Brand وربطه بالمستخدم
        brand = Brand.objects.create(
            user=user,
            brand_name=validated_data['brand_name'],
        )

        return brand


class CreatorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Creator
        fields = [
            'id', 'user', 'bio', 'profile_pic', 'avg_rating', 'total_reviews', 'facebook_followers', 
            'instagram_followers', 'youtube_followers', 'tiktok_followers', 'snapchat_followers', 
            'avg_completion_rate', 'avg_response_speed', 'clients_number', 'services_number', 
            'last_seen', 'register_date', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_seen', 'register_date']

    def get_avg_rating(self, obj):
        return obj.avg_rating()

    def get_total_reviews(self, obj):
        return obj.total_reviews()


    # def get_reviews(self, obj):
    #     reviews = Rating.objects.filter(creator=obj)
    #     return ReviewSerializer(reviews, many=True).data

# لعرض التقييمات بشكل منفصل في قسم Reviews: استخدم CreatorReviewsViewSet مع إعدادات URL خاصة.
# لتضمين التقييمات مباشرة مع بيانات Creator: استخدم SerializerMethodField لتضمين التقييمات.

class CreatorSignUpSerializer(serializers.ModelSerializer):
   # bio = serializers.CharField()
    #profile_pic = serializers.URLField(allow_blank=True, required=False, help_text="URL of the profile picture.")
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    country = serializers.CharField(max_length=50)  # حقل مخصص للمستخدم.
    phone_number = serializers.CharField(max_length=20)  # حقل مخصص للمستخدم.
    
    email = serializers.EmailField()

    class Meta:
        model = Creator
        fields = ['email', 'password', 'confirm_password', 'country', 'phone_number']

    def validate(self, data):
        # تحقق من تطابق كلمتي المرور
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        # إزالة كلمة المرور المؤكدة لأنها غير ضرورية للحفظ
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        phone_number = validated_data.pop('phone_number')
        country = validated_data.pop('country')


        # إنشاء مستخدم جديد
        user = User.objects.create(
            username=email,
            email=email,
            password=password,
        )
        user.country = country
        user.phone_number = phone_number        
        user.save()

        # إنشاء كيان Creator مرتبط بالمستخدم
        creator = Creator.objects.create(
            user=user,
            bio=validated_data.get('bio', ''),
            profile_pic=validated_data.get('profile_pic', None)
        )
        return creator
    

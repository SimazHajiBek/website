from rest_framework import serializers
from .models import Service, ServiceVideo, Category, Content

class ServiceVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for ServiceVideo model.
    """
    class Meta:
        model = ServiceVideo
        fields = ['service', 'video_file', 'description', 'uploaded_at']
        read_only_fields = ['uploaded_at']  # جعل هذه الحقول قراءة فقط


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model.
    """
    videos = ServiceVideoSerializer(many=True, read_only=True)  # إظهار الفيديوهات المرتبطة بهذه الخدمة
    creator = serializers.CharField(max_length=100)

    class Meta:
        model = Service
        fields = [
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
            'videos'
        ]
        read_only_fields = ['created_at', 'updated_at']  # جعل هذه الحقول قراءة فقط

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ContentSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    category = CategorySerializer(many=True)  # تضمين تفاصيل الفئات المرتبطة
    gender = serializers.CharField(source='creator.user.gender', read_only=True)
    voice_over = serializers.BooleanField(source="service.voice_over", read_only=True)
    face_appearing = serializers.BooleanField(source="service.face_appearing", read_only=True)
    price = serializers.DecimalField(source="service.price",max_digits=10, decimal_places=2, read_only=True)
    service = serializers.CharField(source="service.service_name")  # إظهار اسم الخدمة بدلاً من الـ ID

    class Meta:
        model = Content
        fields = [
            'creator', 'category', 'service', 'platform', 
            'title', 'description', 'ugc_type', 'uploaded_at', 'views_count',
            'gender', 'voice_over', 'face_appearing','price'
        ]

class PortfolioContentSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=True)  # يعرض اسم الفئة مباشرة
    price = serializers.DecimalField(source="service.price", max_digits=10, decimal_places=2, read_only=True)  # سعر الخدمة
    creator_image = serializers.ImageField(source='creator.profile_pic', read_only=True)  # صورة الـ Creator (افترضنا وجود حقل صورة في بروفايل المستخدم)
    service_video = serializers.FileField(source='service.videos.first.video_file', read_only=True)  # الفيديو الأول من فيديوهات الخدمة

    class Meta:
        model = Content
        fields = [
            'title', 'description', 'category', 'price', 'creator_image', 'service_video'
        ]

# category:

# يستخدم StringRelatedField لعرض اسم الفئة (بدلاً من عرض تفاصيلها بالكامل).
# price:

# يستخرج سعر الخدمة المرتبطة بـ Content عن طريق العلاقة بين Content و Service.
# creator_image:

# يعرض صورة الـ Creator بناءً على علاقة الـ Creator مع الـ User (يفترض أن هناك حقل صورة في بروفايل المستخدم).
# service_video:

# يستخرج أول فيديو مرتبط بالخدمة باستخدام العلاقة بين Service و ServiceVideo.
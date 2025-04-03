import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_instagram_followers
from .models import User, Brand, Creator
from .serializers import UserSerializer, BrandSerializer, CreatorSerializer, CreatorSignUpSerializer,BrandSignUpSerializer

class UserViewSet(CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,):
    """
    ViewSet لإدارة المستخدمين مع دعم الفلترة، الترتيب، والبحث.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['is_active', 'is_staff']  # الفلترة حسب حالة المستخدم
    ordering_fields = ['date_joined', 'username']  # الترتيب حسب تاريخ الانضمام أو اسم المستخدم
    search_fields = ['username', 'email']  # البحث باستخدام اسم المستخدم أو البريد الإلكتروني
    permission_classes = [IsAuthenticated]



class BrandViewSet(GenericViewSet, UpdateModelMixin):
    """
    ViewSet للتعامل مع بيانات Brand. 
    هل هكذا الجميع يرى المعلومات والبراند فقط تستطيع التعديل؟؟
    """
    #queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Brand.objects.filter(user=self.request.user)
        return Brand.objects.none()

    def get_serializer_class(self):
        """
        استخدم Serializer مختلف لتسجيل الحساب.
        """
        if self.action == 'signup':  # نتحقق إذا كانت العملية تسجيل
            return BrandSignUpSerializer
        return BrandSerializer

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        """
        معالجة تسجيل الحساب الجديد لـ Brand.
        """
        serializer = BrandSignUpSerializer(data=request.data)
        if serializer.is_valid():
            brand = serializer.save()
            return Response(
                {"message": "Brand account created successfully!", "brand_id": brand.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        عرض بيانات حساب الـ Brand الخاص بالمستخدم الحالي.
        """
        brand = Brand.objects.select_related("user").filter(user_id=request.user.id).first()
        print(brand)
        if not brand:
            return Response({"error": "You are not registered as a brand."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BrandSerializer(brand, context={"request": request})
        return Response(serializer.data)



    # @action(detail=False, methods=['put'], url_path='update', permission_classes=[IsAuthenticated])
    # def update(self, request):
    #     """
    #     تحديث بيانات حساب الـ Brand الحالي.
    #     """
    #     brand = Brand.objects.filter(user=request.brand ).first()
    #     if not brand:
    #         return Response(
    #             {"detail": "No Brand found for the current user."},
    #             status=status.HTTP_404_NOT_FOUND
    #         )
    #     serializer = self.get_serializer(brand, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             {"message": "Brand account updated successfully!", "data": serializer.data},
    #             status=status.HTTP_200_OK
    #         )
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatorViewSet(GenericViewSet, UpdateModelMixin):
    """
    ViewSet للتعامل مع Creators.
    """
    queryset = Creator.objects.all()

    #serializer_class = CreatorSerializer

    def get_serializer_class(self):
        """
        اختر السيريالايزر المناسب بناءً على نوع العملية.
        """
        if self.action == 'signup':
            return CreatorSignUpSerializer
        return CreatorSerializer

    @action(detail=False, methods=['post'], permission_classes=[])
    def signup(self, request):
        """
        تسجيل حساب جديد كـ Creator.
        """
        serializer = CreatorSignUpSerializer(data=request.data)
        if serializer.is_valid():
            creator = serializer.save()
            return Response(
                {"message": "Creator account created successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        creator = Creator.objects.select_related("user").filter(user_id=request.user.id).first()

        if not creator:
            return Response({"error": "You are not registered as a creator."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreatorSerializer(creator, context={"request": request})
        return Response(serializer.data)


# def get_instagram_followers(username):
#     url = "https://instagram-data-api.p.rapidapi.com/user/info"
#     querystring = {"username": username}

#     headers = {
#         "X-RapidAPI-Key": "ضع_مفتاحك_هنا",  # استبدله بمفتاحك الحقيقي من RapidAPI
#         "X-RapidAPI-Host": "instagram-data-api.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring)

#     if response.status_code == 200:
#         data = response.json()
#         return data.get("followers", "❌ لم يتم العثور على المتابعين")
#     else:
#         return f"❌ خطأ: {response.status_code}"

@api_view(['GET'])
def get_followers_view(request):
    username = request.GET.get("username", None)  # استخلاص اسم المستخدم من الطلب
    if not username:
        return Response({"error": "يرجى تمرير اسم المستخدم في الطلب."}, status=400)

    followers = get_instagram_followers(username)
    print(f"DEBUG: Followers for {username} = {followers}")

    return Response({"username": username, "followers": followers}, content_type="application/json; charset=utf-8")
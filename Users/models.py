from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

class User(AbstractUser):
    CREATOR = 'creator'
    BRAND = 'brand'
    ROLE_CHOICES = [
        (CREATOR, 'Creator'),
        (BRAND, 'Brand'),
    ]

    id = models.UUIDField(default=uuid4, primary_key=True)
    GENDER_MALE_CHOICE = "M"
    GENDER_FEMALE_CHOICE = "F"
    GENDER_CHOICES = [(GENDER_MALE_CHOICE, "Male"), (GENDER_FEMALE_CHOICE, "Female")]
    first_name = models.CharField(
        "first name", max_length=150 #, validators=[validators.validate_name]
    )
    last_name = models.CharField(
        "last name", max_length=150 #, validators=[validators.validate_name]
    )
    birth_date = models.DateField()#validators=[validators.validate_date])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    country = CountryField(null=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length= 20, null=True)
    #REQUIRED_FIELDS = ["first_name", "last_name","email","gender"]#,"country"]

    def save(self, *args, **kwargs) -> None:
        if self.first_name:
            self.first_name = self.first_name.capitalize()
        if self.last_name:
            self.last_name = self.last_name.capitalize()
        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['user_type', 'email']),  # فهرس مكون من user_type و email

        ]
    def __str__(self):
        return f"{self.username} ({self.email})"
    



class Brand(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="brand")
    brand_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)


    # About
    about_me = models.TextField(help_text="Description of the brand", blank=True)

    # Social Media Stats
    facebook_followers = models.PositiveIntegerField(default=0, help_text="Number of followers on Facebook")
    instagram_followers = models.PositiveIntegerField(default=0, help_text="Number of followers on Instagram")
    youtube_followers = models.PositiveIntegerField(default=0, help_text="Number of followers on YouTube")
    tiktok_followers = models.PositiveIntegerField(default=0, help_text="Number of followers on TikTok")
    snapchat_followers = models.PositiveIntegerField(default=0, help_text="Number of followers on Snapchat")

    # Statistics
    order_number = models.PositiveIntegerField(default=0, help_text="Number of orders made")
    avg_order_time = models.PositiveIntegerField(default=0, help_text="Average order completion time in percentage")
    avg_response_speed = models.CharField(max_length=50, help_text="Average response speed (e.g., '2 hours')", blank=True)
    last_seen = models.DateTimeField(auto_now=True, help_text="Last seen timestamp")
    register_date = models.DateTimeField(auto_now_add=True, help_text="Date of registration")
    #الحقل السابق؟ هل نحتاج الى الحقل اللاحق بوجود 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.brand_name


class Creator(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="creator")
    bio = models.TextField(blank=True, null=True, help_text="A short biography of the creator.")
    profile_pic = models.URLField(blank=True, null=True, help_text="URL of the profile picture.")

    # Social Media Stats
    facebook_followers = models.PositiveIntegerField(default=0)
    instagram_followers = models.PositiveIntegerField(default=0)
    youtube_followers = models.PositiveIntegerField(default=0)
    tiktok_followers = models.PositiveIntegerField(default=0)
    snapchat_followers = models.PositiveIntegerField(default=0)

    # Statistics
#    average_rating = models.FloatField(default=0.0, help_text="Average rating for the creator.")
    avg_completion_rate = models.PositiveIntegerField(default=0, help_text="Average completion rate in percentage")
    avg_response_speed = models.CharField(max_length=50, blank=True, help_text="Average response speed (e.g., '2 hours')")
    clients_number = models.PositiveIntegerField(default=0, help_text="Number of clients")
    services_number = models.PositiveIntegerField(default=0, help_text="Number of services")
    last_seen = models.DateTimeField(auto_now=True, help_text="Last seen timestamp")
    register_date = models.DateTimeField(auto_now_add=True, help_text="Date of registration")
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def avg_rating(self):
        return round(self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0, 1)

    def total_reviews(self):
        return self.reviews.count()
    
    def __str__(self):
        return self.user.username



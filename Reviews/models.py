from uuid import uuid4
from django.db import models
from Users.models import Brand, Creator
from Services.models import ServiceVideo
# Create your models here.


class Review(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="reviews")
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="reviews")
    service_video = models.ForeignKey(ServiceVideo, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField(default=0.0)
    review = models.TextField(help_text="Mandatory review text")  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} by {self.brand} for {self.creator}"

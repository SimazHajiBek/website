from django.db import models
from uuid import uuid4
from Users.models import Brand, Creator
from django.conf import settings


class Chat(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name = 'chats')
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"


class Message(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name= 'messages')
    sender_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    message = models.TextField()
    file = models.FileField(
        upload_to='chat_files/videos/', 
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id}"

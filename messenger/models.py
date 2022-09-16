from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    chat = models.ForeignKey(
        'Chat', on_delete=models.CASCADE, related_name="messages", blank=True, null=True)
    body = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.chat.name}: {self.body}"


class Chat(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    users = models.ManyToManyField(
        User, related_name="chats", blank=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_chats", blank=True, null=True)

    def __str__(self):
        return f"Chat between {[user.username for user in self.users.all()]}"

    def serialize(self):
        return {
            "id": self.id,
            "users": [user.username for user in self.users.all()],
            'messages': [message.serialize() for message in self.messages.all()]
        }

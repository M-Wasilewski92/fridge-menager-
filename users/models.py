from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    friends = models.ManyToManyField('self', blank=True)
    notification_preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return self.email

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Oczekujące'),
        ('accepted', 'Zaakceptowane'),
        ('rejected', 'Odrzucone'),
    ]
    
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sender', 'receiver']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('expiry', 'Data ważności'),
        ('low_stock', 'Niski stan magazynowy'),
        ('wastage', 'Marnowanie'),
        ('report', 'Raport'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, null=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('products.Category', on_delete=models.CASCADE, null=True, blank=True)
    
    # Pola do powiązania z innymi modelami
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Powiadomienie'
        verbose_name_plural = 'Powiadomienia'

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

    def mark_as_read(self):
        self.read = True
        self.save() 
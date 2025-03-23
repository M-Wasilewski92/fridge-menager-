from django.contrib.contenttypes.models import ContentType
from .models import Notification

def create_notification(user, notification_type, title, message, related_object=None):
    """
    Tworzy nowe powiadomienie dla użytkownika.
    
    Args:
        user: Użytkownik, dla którego tworzone jest powiadomienie
        notification_type: Typ powiadomienia (z Notification.NOTIFICATION_TYPES)
        title: Tytuł powiadomienia
        message: Treść powiadomienia
        related_object: Opcjonalny obiekt powiązany z powiadomieniem
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message
    )
    
    if related_object:
        notification.content_type = ContentType.objects.get_for_model(related_object)
        notification.object_id = related_object.pk
        notification.save()
    
    return notification 
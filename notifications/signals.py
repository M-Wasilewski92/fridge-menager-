from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from shopping_list.models import ShoppingList
from .utils import create_notification

@receiver(post_save, sender=Product)
def check_product_expiry(sender, instance, created, **kwargs):
    """Sprawdza datę ważności produktu i tworzy powiadomienie jeśli jest bliska."""
    if not created and instance.expiry_date:
        days_until_expiry = (instance.expiry_date - timezone.now().date()).days
        if days_until_expiry <= 7 and days_until_expiry > 0:
            create_notification(
                user=instance.user,
                notification_type='expiry',
                title='Produkt wkrótce się przeterminuje',
                message=f'Produkt "{instance.name}" przeterminuje się za {days_until_expiry} dni.',
                related_object=instance
            )
        elif days_until_expiry <= 0:
            create_notification(
                user=instance.user,
                notification_type='expiry',
                title='Produkt się przeterminował',
                message=f'Produkt "{instance.name}" się przeterminował.',
                related_object=instance
            )

@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, created, **kwargs):
    """Sprawdza stan magazynowy produktu i tworzy powiadomienie jeśli jest niski."""
    if not created and instance.quantity <= instance.min_quantity:
        create_notification(
            user=instance.user,
            notification_type='low_stock',
            title='Niski stan magazynowy',
            message=f'Produkt "{instance.name}" ma niski stan magazynowy ({instance.quantity} {instance.unit}).',
            related_object=instance
        )

@receiver(post_save, sender=ShoppingList)
def notify_shopping_list_created(sender, instance, created, **kwargs):
    """Tworzy powiadomienie gdy lista zakupów jest tworzona."""
    if created:
        create_notification(
            user=instance.user,
            notification_type='shopping_list',
            title='Nowa lista zakupów',
            message=f'Utworzono nową listę zakupów "{instance.name}".',
            related_object=instance
        ) 
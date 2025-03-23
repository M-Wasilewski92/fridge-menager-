from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Notification
from products.models import Product
from reports.models import ProductWastage

def generate_expiry_notifications(user):
    """Generuje powiadomienia o kończących się produktach."""
    # Produkty, których data ważności kończy się w ciągu 7 dni
    expiry_threshold = timezone.now() + timedelta(days=7)
    
    expiring_products = Product.objects.filter(
        user=user,
        expiry_date__lte=expiry_threshold,
        expiry_date__gt=timezone.now(),
        is_active=True
    )
    
    for product in expiring_products:
        days_left = (product.expiry_date - timezone.now()).days
        Notification.objects.create(
            user=user,
            notification_type='expiry',
            title=f'Kończy się data ważności produktu {product.name}',
            message=f'Produkt {product.name} straci ważność za {days_left} dni.',
            product=product,
            link=f'/products/{product.id}/'
        )

def generate_low_stock_notifications(user):
    """Generuje powiadomienia o niskim stanie magazynowym."""
    # Produkty z ilością mniejszą niż 1 jednostka
    low_stock_products = Product.objects.filter(
        user=user,
        quantity__lte=1,
        is_active=True
    )
    
    for product in low_stock_products:
        Notification.objects.create(
            user=user,
            notification_type='low_stock',
            title=f'Niski stan magazynowy produktu {product.name}',
            message=f'Produkt {product.name} ma niski stan magazynowy ({product.quantity} {product.unit}).',
            product=product,
            link=f'/products/{product.id}/'
        )

def generate_wastage_notifications(user):
    """Generuje powiadomienia o marnowaniu produktów."""
    # Produkty, które zostały oznaczone jako marnowane w ciągu ostatnich 24 godzin
    wastage_threshold = timezone.now() - timedelta(days=1)
    
    recent_wastages = ProductWastage.objects.filter(
        user=user,
        wastage_date__gte=wastage_threshold
    )
    
    for wastage in recent_wastages:
        Notification.objects.create(
            user=user,
            notification_type='wastage',
            title=f'Marnowanie produktu {wastage.product.name}',
            message=f'Produkt {wastage.product.name} został oznaczony jako marnowany. Powód: {wastage.reason}',
            product=wastage.product,
            link=f'/products/{wastage.product.id}/'
        )

def generate_report_notifications(user):
    """Generuje powiadomienia podsumowujące raporty."""
    # Sprawdź, czy są jakieś istotne statystyki do zgłoszenia
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Sprawdź marnowanie
    wastage_count = ProductWastage.objects.filter(
        user=user,
        wastage_date__gte=thirty_days_ago
    ).count()
    
    if wastage_count > 0:
        Notification.objects.create(
            user=user,
            notification_type='report',
            title='Podsumowanie marnowania produktów',
            message=f'W ciągu ostatnich 30 dni odnotowano {wastage_count} przypadków marnowania produktów.',
            link='/reports/wastage/'
        )

def generate_all_notifications(user):
    """Generuje wszystkie typy powiadomień."""
    generate_expiry_notifications(user)
    generate_low_stock_notifications(user)
    generate_wastage_notifications(user)
    generate_report_notifications(user) 
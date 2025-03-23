from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from notifications.models import Notification
from .models import ShoppingExpense, ProductWastage
from products.models import ProductConsumption

def check_budget_exceeded(user, threshold=1000):
    """
    Sprawdza czy wydatki przekroczyły próg budżetowy w ostatnich 30 dniach.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_expenses = ShoppingExpense.objects.filter(
        user=user,
        shopping_date__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    if total_expenses > threshold:
        Notification.objects.create(
            user=user,
            title='Przekroczono próg budżetowy',
            message=f'W ostatnich 30 dniach wydano {total_expenses:.2f} zł, co przekracza próg {threshold} zł.',
            notification_type='budget'
        )

def check_high_wastage(user, threshold=5):
    """
    Sprawdza czy marnowanie produktów przekroczyło próg w ostatnich 30 dniach.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_wastage = ProductWastage.objects.filter(
        user=user,
        wastage_date__gte=thirty_days_ago
    ).count()

    if total_wastage > threshold:
        Notification.objects.create(
            user=user,
            title='Wysokie marnowanie produktów',
            message=f'W ostatnich 30 dniach odnotowano {total_wastage} przypadków marnowania produktów, co przekracza próg {threshold}.',
            notification_type='wastage'
        )

def check_consumption_trends(user):
    """
    Sprawdza trendy zużycia produktów i generuje powiadomienia o znaczących zmianach.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    fifteen_days_ago = timezone.now() - timedelta(days=15)

    # Oblicz zużycie w pierwszej połowie okresu
    first_half = ProductConsumption.objects.filter(
        user=user,
        consumption_date__gte=thirty_days_ago,
        consumption_date__lt=fifteen_days_ago
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Oblicz zużycie w drugiej połowie okresu
    second_half = ProductConsumption.objects.filter(
        user=user,
        consumption_date__gte=fifteen_days_ago
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Jeśli zużycie wzrosło o więcej niż 50%
    if second_half > first_half * 1.5:
        Notification.objects.create(
            user=user,
            title='Znaczący wzrost zużycia',
            message='W ostatnich 15 dniach odnotowano znaczący wzrost zużycia produktów w porównaniu do poprzednich 15 dni.',
            notification_type='consumption'
        )
    # Jeśli zużycie spadło o więcej niż 50%
    elif second_half < first_half * 0.5:
        Notification.objects.create(
            user=user,
            title='Znaczący spadek zużycia',
            message='W ostatnich 15 dniach odnotowano znaczący spadek zużycia produktów w porównaniu do poprzednich 15 dni.',
            notification_type='consumption'
        )

def generate_report_notifications(user):
    """
    Generuje wszystkie powiadomienia związane z raportami.
    """
    check_budget_exceeded(user)
    check_high_wastage(user)
    check_consumption_trends(user) 
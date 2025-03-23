from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ReportsEdgeCasesTests(TestCase):
    def setUp(self):
        # Tworzenie użytkownika
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Tworzenie kategorii
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        
        # Tworzenie produktu
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            unit='szt',
            barcode='123456789'
        )
        
        # Tworzenie listy zakupów
        self.shopping_list = ShoppingList.objects.create(
            name='Test List',
            user=self.user
        )
        
        # Klient testowy
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_empty_dashboard(self):
        """Test dashboardu bez danych"""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/dashboard.html')
        
        # Sprawdzanie komunikatów o braku danych
        self.assertContains(response, 'Brak danych')
        self.assertContains(response, 'Dodaj pierwszy wpis')

    def test_large_numbers(self):
        """Test dużych wartości liczbowych"""
        # Test dużych ilości
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=999999.99,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Test dużych kwot
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=Decimal('999999.99'),
            shopping_date=timezone.now()
        )
        
        # Sprawdzanie wyświetlania
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, str(consumption.quantity))
        self.assertContains(response, str(expense.total_amount))

    def test_special_characters(self):
        """Test znaków specjalnych w tekstach"""
        # Test w nazwie produktu
        self.product.name = 'Test!@#$%^&*()_+'
        self.product.save()
        
        # Test w przyczynie marnowania
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Test!@#$%^&*()_+'
        )
        
        # Sprawdzanie wyświetlania
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, self.product.name)
        self.assertContains(response, wastage.reason)

    def test_long_texts(self):
        """Test długich tekstów"""
        # Test długiej nazwy produktu
        self.product.name = 'A' * 100
        self.product.save()
        
        # Test długiej przyczyny marnowania
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='A' * 500
        )
        
        # Sprawdzanie wyświetlania
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, self.product.name[:50])  # Sprawdzanie skrócenia
        self.assertContains(response, wastage.reason[:200])  # Sprawdzanie skrócenia

    def test_many_records(self):
        """Test dużej liczby rekordów"""
        # Tworzenie 100 rekordów
        for i in range(100):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.product,
                quantity=1.0,
                unit='szt',
                consumption_date=timezone.now() - timedelta(days=i)
            )
        
        # Sprawdzanie paginacji
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Strona 1 z')

    def test_dates_edge_cases(self):
        """Test przypadków brzegowych dat"""
        # Test bardzo starej daty
        old_date = timezone.now() - timedelta(days=365)
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            consumption_date=old_date
        )
        
        # Test daty z przyszłości (powinno się nie udać)
        with self.assertRaises(ValidationError):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.product,
                quantity=1.0,
                unit='szt',
                consumption_date=timezone.now() + timedelta(days=1)
            )

    def test_decimal_precision(self):
        """Test precyzji liczb dziesiętnych"""
        # Test bardzo małych liczb
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=0.0001,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Test bardzo dużych liczb
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=Decimal('999999.9999'),
            shopping_date=timezone.now()
        )
        
        # Sprawdzanie wyświetlania
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, str(consumption.quantity))
        self.assertContains(response, str(expense.total_amount)) 
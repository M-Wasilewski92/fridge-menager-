from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ReportsUITests(TestCase):
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

    def test_dashboard_ui(self):
        """Test interfejsu dashboardu"""
        response = self.client.get(reverse('reports:dashboard'))
        
        # Sprawdzanie nagłówka
        self.assertContains(response, 'Dashboard')
        
        # Sprawdzanie sekcji statystyk
        self.assertContains(response, 'Statystyki')
        self.assertContains(response, 'Zużycie produktów')
        self.assertContains(response, 'Wydatki')
        self.assertContains(response, 'Marnowanie')
        
        # Sprawdzanie wykresów
        self.assertContains(response, 'expenseTrends')
        self.assertContains(response, 'consumptionTrends')
        self.assertContains(response, 'wastageTrends')
        
        # Sprawdzanie przycisków akcji
        self.assertContains(response, 'Dodaj zużycie')
        self.assertContains(response, 'Dodaj wydatek')
        self.assertContains(response, 'Dodaj marnowanie')

    def test_consumption_form_ui(self):
        """Test interfejsu formularza zużycia"""
        response = self.client.get(reverse('reports:add_consumption'))
        
        # Sprawdzanie nagłówka
        self.assertContains(response, 'Dodaj zużycie produktu')
        
        # Sprawdzanie pól formularza
        self.assertContains(response, 'name="product"')
        self.assertContains(response, 'name="quantity"')
        self.assertContains(response, 'name="unit"')
        self.assertContains(response, 'name="consumption_date"')
        
        # Sprawdzanie przycisków
        self.assertContains(response, 'Zapisz')
        self.assertContains(response, 'Anuluj')

    def test_expense_form_ui(self):
        """Test interfejsu formularza wydatków"""
        response = self.client.get(reverse('reports:add_expense'))
        
        # Sprawdzanie nagłówka
        self.assertContains(response, 'Dodaj wydatek')
        
        # Sprawdzanie pól formularza
        self.assertContains(response, 'name="shopping_list"')
        self.assertContains(response, 'name="total_amount"')
        self.assertContains(response, 'name="shopping_date"')
        
        # Sprawdzanie przycisków
        self.assertContains(response, 'Zapisz')
        self.assertContains(response, 'Anuluj')

    def test_wastage_form_ui(self):
        """Test interfejsu formularza marnowania"""
        response = self.client.get(reverse('reports:add_wastage'))
        
        # Sprawdzanie nagłówka
        self.assertContains(response, 'Dodaj marnowanie')
        
        # Sprawdzanie pól formularza
        self.assertContains(response, 'name="product"')
        self.assertContains(response, 'name="quantity"')
        self.assertContains(response, 'name="unit"')
        self.assertContains(response, 'name="wastage_date"')
        self.assertContains(response, 'name="reason"')
        
        # Sprawdzanie przycisków
        self.assertContains(response, 'Zapisz')
        self.assertContains(response, 'Anuluj')

    def test_report_ui(self):
        """Test interfejsu raportów"""
        # Test raportu wydatków
        response = self.client.get(reverse('reports:expense_report'))
        self.assertContains(response, 'Raport wydatków')
        self.assertContains(response, 'Tabela wydatków')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')
        
        # Test raportu zużycia
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertContains(response, 'Raport zużycia')
        self.assertContains(response, 'Tabela zużycia')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')
        
        # Test raportu marnowania
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, 'Raport marnowania')
        self.assertContains(response, 'Tabela marnowania')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')

    def test_form_validation_ui(self):
        """Test interfejsu walidacji formularzy"""
        # Test pustego formularza zużycia
        response = self.client.post(reverse('reports:add_consumption'), {})
        self.assertContains(response, 'To pole jest wymagane')
        
        # Test pustego formularza wydatków
        response = self.client.post(reverse('reports:add_expense'), {})
        self.assertContains(response, 'To pole jest wymagane')
        
        # Test pustego formularza marnowania
        response = self.client.post(reverse('reports:add_wastage'), {})
        self.assertContains(response, 'To pole jest wymagane')

    def test_navigation_ui(self):
        """Test nawigacji w interfejsie"""
        # Test przycisku powrotu do dashboardu
        response = self.client.get(reverse('reports:add_consumption'))
        self.assertContains(response, 'Powrót do dashboardu')
        
        response = self.client.get(reverse('reports:add_expense'))
        self.assertContains(response, 'Powrót do dashboardu')
        
        response = self.client.get(reverse('reports:add_wastage'))
        self.assertContains(response, 'Powrót do dashboardu')
        
        # Test nawigacji między raportami
        response = self.client.get(reverse('reports:expense_report'))
        self.assertContains(response, 'Raport zużycia')
        self.assertContains(response, 'Raport marnowania')
        
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertContains(response, 'Raport wydatków')
        self.assertContains(response, 'Raport marnowania')
        
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, 'Raport wydatków')
        self.assertContains(response, 'Raport zużycia') 
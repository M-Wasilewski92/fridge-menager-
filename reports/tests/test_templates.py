from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ReportsTemplatesTests(TestCase):
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
        
        # Tworzenie przykładowych danych
        self.consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        self.expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        self.wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        # Klient testowy
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_template(self):
        """Test szablonu dashboardu"""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertTemplateUsed(response, 'reports/dashboard.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Statystyki')
        self.assertContains(response, 'Wykresy')
        self.assertContains(response, 'Top produkty')

    def test_consumption_form_template(self):
        """Test szablonu formularza zużycia"""
        response = self.client.get(reverse('reports:add_consumption'))
        self.assertTemplateUsed(response, 'reports/consumption_form.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Dodaj zużycie')
        self.assertContains(response, 'Produkt')
        self.assertContains(response, 'Ilość')
        self.assertContains(response, 'Jednostka')
        self.assertContains(response, 'Data zużycia')

    def test_expense_form_template(self):
        """Test szablonu formularza wydatków"""
        response = self.client.get(reverse('reports:add_expense'))
        self.assertTemplateUsed(response, 'reports/expense_form.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Dodaj wydatek')
        self.assertContains(response, 'Lista zakupów')
        self.assertContains(response, 'Kwota')
        self.assertContains(response, 'Data zakupów')

    def test_wastage_form_template(self):
        """Test szablonu formularza marnowania"""
        response = self.client.get(reverse('reports:add_wastage'))
        self.assertTemplateUsed(response, 'reports/wastage_form.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Dodaj marnowanie')
        self.assertContains(response, 'Produkt')
        self.assertContains(response, 'Ilość')
        self.assertContains(response, 'Jednostka')
        self.assertContains(response, 'Data marnowania')
        self.assertContains(response, 'Przyczyna')

    def test_expense_report_template(self):
        """Test szablonu raportu wydatków"""
        response = self.client.get(reverse('reports:expense_report'))
        self.assertTemplateUsed(response, 'reports/expense_report.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Raport wydatków')
        self.assertContains(response, 'Suma wydatków')
        self.assertContains(response, 'Średnia wydatków')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')

    def test_consumption_report_template(self):
        """Test szablonu raportu zużycia"""
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertTemplateUsed(response, 'reports/consumption_report.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Raport zużycia')
        self.assertContains(response, 'Suma zużycia')
        self.assertContains(response, 'Średnie zużycie')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')

    def test_wastage_report_template(self):
        """Test szablonu raportu marnowania"""
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertTemplateUsed(response, 'reports/wastage_report.html')
        
        # Sprawdzanie obecności elementów
        self.assertContains(response, 'Raport marnowania')
        self.assertContains(response, 'Suma marnowania')
        self.assertContains(response, 'Średnie marnowanie')
        self.assertContains(response, 'Eksportuj CSV')
        self.assertContains(response, 'Eksportuj PDF')

    def test_pdf_templates(self):
        """Test szablonów PDF"""
        # Test szablonu PDF dla wydatków
        response = self.client.get(reverse('reports:export_expense_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Test szablonu PDF dla zużycia
        response = self.client.get(reverse('reports:export_consumption_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Test szablonu PDF dla marnowania
        response = self.client.get(reverse('reports:export_wastage_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_expense_report_table_data(self):
        """Test wyświetlania danych w tabeli wydatków"""
        response = self.client.get(reverse('reports:expense_report'))
        
        # Sprawdzanie wyświetlania danych
        self.assertContains(response, str(self.expense.total_amount))
        self.assertContains(response, self.expense.shopping_list.name)
        self.assertContains(response, self.expense.shopping_date.strftime('%Y-%m-%d'))

    def test_consumption_report_table_data(self):
        """Test wyświetlania danych w tabeli zużycia"""
        response = self.client.get(reverse('reports:consumption_report'))
        
        # Sprawdzanie wyświetlania danych
        self.assertContains(response, str(self.consumption.quantity))
        self.assertContains(response, self.consumption.product.name)
        self.assertContains(response, self.consumption.consumption_date.strftime('%Y-%m-%d'))

    def test_wastage_report_table_data(self):
        """Test wyświetlania danych w tabeli marnowania"""
        response = self.client.get(reverse('reports:wastage_report'))
        
        # Sprawdzanie wyświetlania danych
        self.assertContains(response, str(self.wastage.quantity))
        self.assertContains(response, self.wastage.product.name)
        self.assertContains(response, self.wastage.wastage_date.strftime('%Y-%m-%d'))
        self.assertContains(response, self.wastage.reason) 
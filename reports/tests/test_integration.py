from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage
from .forms import ProductConsumptionForm, ShoppingExpenseForm, ProductWastageForm

User = get_user_model()

class ReportsIntegrationTests(TestCase):
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

    def test_full_consumption_flow(self):
        """Test pełnego przepływu dodawania zużycia produktu"""
        # 1. Dodanie zużycia produktu
        consumption_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        
        response = self.client.post(
            reverse('reports:add_consumption'),
            consumption_data
        )
        self.assertEqual(response.status_code, 302)  # Przekierowanie po sukcesie
        
        # 2. Sprawdzenie czy zużycie zostało dodane
        consumption = ProductConsumption.objects.get(user=self.user)
        self.assertEqual(consumption.quantity, 2.5)
        self.assertEqual(consumption.unit, 'szt')
        
        # 3. Sprawdzenie czy dane są widoczne w raporcie
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertContains(response, 'Test Product')
        self.assertContains(response, '2.5 szt')

    def test_full_expense_flow(self):
        """Test pełnego przepływu dodawania wydatku"""
        # 1. Dodanie wydatku
        expense_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        
        response = self.client.post(
            reverse('reports:add_expense'),
            expense_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 2. Sprawdzenie czy wydatek został dodany
        expense = ShoppingExpense.objects.get(user=self.user)
        self.assertEqual(expense.total_amount, 100.50)
        
        # 3. Sprawdzenie czy dane są widoczne w raporcie
        response = self.client.get(reverse('reports:expense_report'))
        self.assertContains(response, 'Test List')
        self.assertContains(response, '100.50 zł')

    def test_full_wastage_flow(self):
        """Test pełnego przepływu dodawania marnowania"""
        # 1. Dodanie marnowania
        wastage_data = {
            'product': self.product.id,
            'quantity': 1.0,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Przeterminowany'
        }
        
        response = self.client.post(
            reverse('reports:add_wastage'),
            wastage_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 2. Sprawdzenie czy marnowanie zostało dodane
        wastage = ProductWastage.objects.get(user=self.user)
        self.assertEqual(wastage.quantity, 1.0)
        self.assertEqual(wastage.reason, 'Przeterminowany')
        
        # 3. Sprawdzenie czy dane są widoczne w raporcie
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Przeterminowany')

    def test_dashboard_data_integration(self):
        """Test integracji danych w dashboardzie"""
        # 1. Dodanie danych testowych
        ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        # 2. Sprawdzenie czy dane są poprawnie wyświetlane w dashboardzie
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Test List')
        self.assertContains(response, '100.50 zł')
        self.assertContains(response, '2.5 szt')
        self.assertContains(response, '1.0 szt')

    def test_reports_integration(self):
        """Test integracji raportów"""
        # 1. Dodanie danych testowych
        for i in range(5):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.product,
                quantity=2.5,
                unit='szt',
                consumption_date=timezone.now() - timedelta(days=i)
            )
            
            ShoppingExpense.objects.create(
                user=self.user,
                shopping_list=self.shopping_list,
                total_amount=100.50,
                shopping_date=timezone.now() - timedelta(days=i)
            )
            
            ProductWastage.objects.create(
                user=self.user,
                product=self.product,
                quantity=1.0,
                unit='szt',
                wastage_date=timezone.now() - timedelta(days=i),
                reason='Przeterminowany'
            )
        
        # 2. Sprawdzenie raportu wydatków
        response = self.client.get(reverse('reports:expense_report'))
        self.assertContains(response, '502.50 zł')  # 5 * 100.50
        
        # 3. Sprawdzenie raportu zużycia
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertContains(response, '12.5 szt')  # 5 * 2.5
        
        # 4. Sprawdzenie raportu marnowania
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertContains(response, '5.0 szt')  # 5 * 1.0 
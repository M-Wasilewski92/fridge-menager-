from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage
import json

User = get_user_model()

class ReportsAPITests(TestCase):
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

    def test_expense_trends_api(self):
        """Test API trendów wydatków"""
        # Dodanie danych testowych
        for i in range(5):
            ShoppingExpense.objects.create(
                user=self.user,
                shopping_list=self.shopping_list,
                total_amount=100.50,
                shopping_date=timezone.now() - timedelta(days=i)
            )
        
        # Pobranie danych z API
        response = self.client.get(reverse('reports:expense_trends_api'))
        
        # Sprawdzanie statusu odpowiedzi
        self.assertEqual(response.status_code, 200)
        
        # Sprawdzanie formatu odpowiedzi
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        
        # Sprawdzanie danych
        self.assertEqual(len(data['labels']), 5)  # 5 dni
        self.assertEqual(len(data['datasets'][0]['data']), 5)
        self.assertEqual(data['datasets'][0]['data'][0], 100.50)

    def test_consumption_trends_api(self):
        """Test API trendów zużycia"""
        # Dodanie danych testowych
        for i in range(5):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.product,
                quantity=2.5,
                unit='szt',
                consumption_date=timezone.now() - timedelta(days=i)
            )
        
        # Pobranie danych z API
        response = self.client.get(reverse('reports:consumption_trends_api'))
        
        # Sprawdzanie statusu odpowiedzi
        self.assertEqual(response.status_code, 200)
        
        # Sprawdzanie formatu odpowiedzi
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        
        # Sprawdzanie danych
        self.assertEqual(len(data['labels']), 5)  # 5 dni
        self.assertEqual(len(data['datasets'][0]['data']), 5)
        self.assertEqual(data['datasets'][0]['data'][0], 2.5)

    def test_wastage_trends_api(self):
        """Test API trendów marnowania"""
        # Dodanie danych testowych
        for i in range(5):
            ProductWastage.objects.create(
                user=self.user,
                product=self.product,
                quantity=1.0,
                unit='szt',
                wastage_date=timezone.now() - timedelta(days=i),
                reason='Przeterminowany'
            )
        
        # Pobranie danych z API
        response = self.client.get(reverse('reports:wastage_trends_api'))
        
        # Sprawdzanie statusu odpowiedzi
        self.assertEqual(response.status_code, 200)
        
        # Sprawdzanie formatu odpowiedzi
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        
        # Sprawdzanie danych
        self.assertEqual(len(data['labels']), 5)  # 5 dni
        self.assertEqual(len(data['datasets'][0]['data']), 5)
        self.assertEqual(data['datasets'][0]['data'][0], 1.0)

    def test_api_empty_data(self):
        """Test API z pustymi danymi"""
        # Test trendów wydatków
        response = self.client.get(reverse('reports:expense_trends_api'))
        data = json.loads(response.content)
        self.assertEqual(len(data['datasets'][0]['data']), 0)
        
        # Test trendów zużycia
        response = self.client.get(reverse('reports:consumption_trends_api'))
        data = json.loads(response.content)
        self.assertEqual(len(data['datasets'][0]['data']), 0)
        
        # Test trendów marnowania
        response = self.client.get(reverse('reports:wastage_trends_api'))
        data = json.loads(response.content)
        self.assertEqual(len(data['datasets'][0]['data']), 0)

    def test_api_date_range(self):
        """Test API z różnymi zakresami dat"""
        # Dodanie danych z różnych okresów
        ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now() - timedelta(days=40)  # Poza zakresem
        )
        
        ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=200.50,
            shopping_date=timezone.now() - timedelta(days=15)  # W zakresie
        )
        
        # Pobranie danych z API
        response = self.client.get(reverse('reports:expense_trends_api'))
        data = json.loads(response.content)
        
        # Sprawdzanie czy tylko dane z ostatnich 30 dni są zwracane
        self.assertEqual(len(data['datasets'][0]['data']), 1)
        self.assertEqual(data['datasets'][0]['data'][0], 200.50)

    def test_api_data_aggregation(self):
        """Test agregacji danych w API"""
        # Dodanie wielu wpisów z tego samego dnia
        for _ in range(3):
            ShoppingExpense.objects.create(
                user=self.user,
                shopping_list=self.shopping_list,
                total_amount=100.50,
                shopping_date=timezone.now()
            )
        
        # Pobranie danych z API
        response = self.client.get(reverse('reports:expense_trends_api'))
        data = json.loads(response.content)
        
        # Sprawdzanie czy dane są poprawnie agregowane
        self.assertEqual(len(data['datasets'][0]['data']), 1)
        self.assertEqual(data['datasets'][0]['data'][0], 301.50)  # 3 * 100.50

    def test_api_unauthorized_access(self):
        """Test dostępu do API bez autoryzacji"""
        self.client.logout()
        
        # Test dostępu do API trendów
        response = self.client.get(reverse('reports:expense_trends_api'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:consumption_trends_api'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:wastage_trends_api'))
        self.assertEqual(response.status_code, 302)

    def test_api_data_format(self):
        """Test formatu danych zwracanych przez API"""
        # Tworzenie danych testowych
        ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        # Pobieranie danych z API
        response = self.client.get(reverse('reports:expense_trends_api'))
        data = json.loads(response.content)
        
        # Sprawdzanie struktury danych
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['labels'], list)
        self.assertIsInstance(data['datasets'], list)
        self.assertIsInstance(data['labels'][0], str)
        self.assertIsInstance(data['datasets'][0]['data'], list)
        self.assertIsInstance(data['datasets'][0]['data'][0], (int, float)) 
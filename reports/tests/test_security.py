from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ReportsSecurityTests(TestCase):
    def setUp(self):
        # Tworzenie dwóch użytkowników
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass456'
        )
        
        # Tworzenie kategorii dla user1
        self.category1 = Category.objects.create(
            name='Category 1',
            description='Description 1'
        )
        
        # Tworzenie produktu dla user1
        self.product1 = Product.objects.create(
            name='Product 1',
            category=self.category1,
            unit='szt',
            barcode='123456789'
        )
        
        # Tworzenie listy zakupów dla user1
        self.shopping_list1 = ShoppingList.objects.create(
            name='List 1',
            user=self.user1
        )
        
        # Tworzenie danych testowych dla user1
        self.consumption1 = ProductConsumption.objects.create(
            user=self.user1,
            product=self.product1,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        self.expense1 = ShoppingExpense.objects.create(
            user=self.user1,
            shopping_list=self.shopping_list1,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        self.wastage1 = ProductWastage.objects.create(
            user=self.user1,
            product=self.product1,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        # Klient testowy
        self.client = Client()

    def test_unauthorized_access(self):
        """Test dostępu bez autoryzacji"""
        # Test dostępu do dashboardu
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 302)  # Przekierowanie do logowania
        
        # Test dostępu do raportów
        response = self.client.get(reverse('reports:expense_report'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do formularzy
        response = self.client.get(reverse('reports:add_consumption'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:add_expense'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:add_wastage'))
        self.assertEqual(response.status_code, 302)

    def test_cross_user_access(self):
        """Test dostępu do danych innego użytkownika"""
        # Logowanie jako user2
        self.client.login(username='user2', password='pass456')
        
        # Próba dostępu do danych user1
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Product 1')
        
        # Próba dostępu do raportów user1
        response = self.client.get(reverse('reports:expense_report'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'List 1')
        
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Product 1')
        
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Product 1')

    def test_data_isolation(self):
        """Test izolacji danych między użytkownikami"""
        # Logowanie jako user1
        self.client.login(username='user1', password='pass123')
        
        # Sprawdzanie dostępu do własnych danych
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, 'Product 1')
        self.assertContains(response, 'List 1')
        
        # Logowanie jako user2
        self.client.login(username='user2', password='pass456')
        
        # Sprawdzanie braku dostępu do danych user1
        response = self.client.get(reverse('reports:dashboard'))
        self.assertNotContains(response, 'Product 1')
        self.assertNotContains(response, 'List 1')

    def test_form_security(self):
        """Test bezpieczeństwa formularzy"""
        # Logowanie jako user2
        self.client.login(username='user2', password='pass456')
        
        # Próba dodania zużycia z produktem user1
        data = {
            'product': self.product1.id,  # Produkt należący do user1
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('reports:add_consumption'), data)
        self.assertEqual(response.status_code, 403)  # Brak dostępu
        
        # Próba dodania wydatku z listą user1
        data = {
            'shopping_list': self.shopping_list1.id,  # Lista należąca do user1
            'total_amount': 100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('reports:add_expense'), data)
        self.assertEqual(response.status_code, 403)  # Brak dostępu

    def test_api_security(self):
        """Test bezpieczeństwa API"""
        # Test dostępu do API bez autoryzacji
        response = self.client.get(reverse('reports:expense_trends_api'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:consumption_trends_api'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('reports:wastage_trends_api'))
        self.assertEqual(response.status_code, 302)
        
        # Logowanie jako user2
        self.client.login(username='user2', password='pass456')
        
        # Test dostępu do API z autoryzacją
        response = self.client.get(reverse('reports:expense_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'List 1')
        
        response = self.client.get(reverse('reports:consumption_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Product 1')
        
        response = self.client.get(reverse('reports:wastage_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Product 1') 
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import connection
from django.db.models import Sum
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage
import time
import psutil
import os

User = get_user_model()

class ReportsPerformanceTests(TestCase):
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
        
        # Tworzenie produktów
        self.products = []
        for i in range(100):
            product = Product.objects.create(
                name=f'Test Product {i}',
                category=self.category,
                unit='szt',
                barcode=f'123456789{i}'
            )
            self.products.append(product)
        
        # Tworzenie list zakupów
        self.shopping_lists = []
        for i in range(10):
            shopping_list = ShoppingList.objects.create(
                name=f'Test List {i}',
                user=self.user
            )
            self.shopping_lists.append(shopping_list)
        
        # Tworzenie danych testowych
        for i in range(1000):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.products[i % 100],
                quantity=2.5,
                unit='szt',
                consumption_date=timezone.now() - timedelta(days=i)
            )
            
            ShoppingExpense.objects.create(
                user=self.user,
                shopping_list=self.shopping_lists[i % 10],
                total_amount=100.50,
                shopping_date=timezone.now() - timedelta(days=i)
            )
            
            ProductWastage.objects.create(
                user=self.user,
                product=self.products[i % 100],
                quantity=1.0,
                unit='szt',
                wastage_date=timezone.now() - timedelta(days=i),
                reason='Przeterminowany'
            )
        
        # Klient testowy
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_performance(self):
        """Test wydajności dashboardu"""
        # Pomiar czasu wykonania
        start_time = time.time()
        
        # Pobieranie danych
        response = self.client.get(reverse('reports:dashboard'))
        
        # Sprawdzanie czasu wykonania
        execution_time = time.time() - start_time
        self.assertLess(execution_time, 1.0)  # Maksymalny czas 1 sekunda
        
        # Sprawdzanie liczby zapytań
        self.assertLess(len(connection.queries), 10)  # Maksymalnie 10 zapytań

    def test_report_performance(self):
        """Test wydajności raportów"""
        # Test raportu wydatków
        start_time = time.time()
        response = self.client.get(reverse('reports:expense_report'))
        expense_time = time.time() - start_time
        self.assertLess(expense_time, 1.0)
        
        # Test raportu zużycia
        start_time = time.time()
        response = self.client.get(reverse('reports:consumption_report'))
        consumption_time = time.time() - start_time
        self.assertLess(consumption_time, 1.0)
        
        # Test raportu marnowania
        start_time = time.time()
        response = self.client.get(reverse('reports:wastage_report'))
        wastage_time = time.time() - start_time
        self.assertLess(wastage_time, 1.0)

    def test_export_performance(self):
        """Test wydajności eksportu"""
        # Test eksportu CSV
        start_time = time.time()
        response = self.client.get(reverse('reports:export_expense_csv'))
        csv_time = time.time() - start_time
        self.assertLess(csv_time, 2.0)  # Maksymalny czas 2 sekundy
        
        # Test eksportu PDF
        start_time = time.time()
        response = self.client.get(reverse('reports:export_expense_pdf'))
        pdf_time = time.time() - start_time
        self.assertLess(pdf_time, 3.0)  # Maksymalny czas 3 sekundy

    def test_memory_usage(self):
        """Test użycia pamięci"""
        process = psutil.Process(os.getpid())
        
        # Pomiar pamięci przed operacją
        initial_memory = process.memory_info().rss
        
        # Wykonanie operacji
        response = self.client.get(reverse('reports:dashboard'))
        
        # Pomiar pamięci po operacji
        final_memory = process.memory_info().rss
        
        # Sprawdzanie wzrostu pamięci
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 50 * 1024 * 1024)  # Maksymalny wzrost 50MB

    def test_database_queries(self):
        """Test liczby zapytań do bazy danych"""
        # Test dashboardu
        with self.assertNumQueries(less_than=10):
            self.client.get(reverse('reports:dashboard'))
        
        # Test raportu wydatków
        with self.assertNumQueries(less_than=5):
            self.client.get(reverse('reports:expense_report'))
        
        # Test raportu zużycia
        with self.assertNumQueries(less_than=5):
            self.client.get(reverse('reports:consumption_report'))
        
        # Test raportu marnowania
        with self.assertNumQueries(less_than=5):
            self.client.get(reverse('reports:wastage_report'))

    def test_large_data_handling(self):
        """Test obsługi dużych zbiorów danych"""
        # Tworzenie dużej liczby rekordów
        for i in range(10000):
            ProductConsumption.objects.create(
                user=self.user,
                product=self.products[i % 100],
                quantity=2.5,
                unit='szt',
                consumption_date=timezone.now() - timedelta(days=i)
            )
        
        # Test wydajności agregacji
        start_time = time.time()
        total = ProductConsumption.objects.filter(user=self.user).aggregate(Sum('quantity'))
        execution_time = time.time() - start_time
        self.assertLess(execution_time, 2.0)  # Maksymalny czas 2 sekundy 
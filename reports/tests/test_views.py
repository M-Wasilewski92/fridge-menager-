from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ReportsViewsTests(TestCase):
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

    def test_dashboard_view(self):
        """Test widoku dashboardu"""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/dashboard.html')
        self.assertIn('total_expenses', response.context)
        self.assertIn('total_consumption', response.context)
        self.assertIn('total_wastage', response.context)
        self.assertIn('expense_trends', response.context)
        self.assertIn('consumption_trends', response.context)
        self.assertIn('wastage_trends', response.context)

    def test_add_consumption_view(self):
        """Test widoku dodawania zużycia"""
        # Test GET
        response = self.client.get(reverse('reports:add_consumption'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/consumption_form.html')
        
        # Test POST
        data = {
            'product': self.product.id,
            'quantity': 3.0,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('reports:add_consumption'), data)
        self.assertRedirects(response, reverse('reports:dashboard'))
        
        # Sprawdzanie czy obiekt został utworzony
        self.assertTrue(ProductConsumption.objects.filter(quantity=3.0).exists())

    def test_add_expense_view(self):
        """Test widoku dodawania wydatku"""
        # Test GET
        response = self.client.get(reverse('reports:add_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/expense_form.html')
        
        # Test POST
        data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 150.75,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('reports:add_expense'), data)
        self.assertRedirects(response, reverse('reports:dashboard'))
        
        # Sprawdzanie czy obiekt został utworzony
        self.assertTrue(ShoppingExpense.objects.filter(total_amount=150.75).exists())

    def test_add_wastage_view(self):
        """Test widoku dodawania marnowania"""
        # Test GET
        response = self.client.get(reverse('reports:add_wastage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/wastage_form.html')
        
        # Test POST
        data = {
            'product': self.product.id,
            'quantity': 2.0,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Uszkodzony'
        }
        response = self.client.post(reverse('reports:add_wastage'), data)
        self.assertRedirects(response, reverse('reports:dashboard'))
        
        # Sprawdzanie czy obiekt został utworzony
        self.assertTrue(ProductWastage.objects.filter(quantity=2.0).exists())

    def test_expense_report_view(self):
        """Test widoku raportu wydatków"""
        response = self.client.get(reverse('reports:expense_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/expense_report.html')
        self.assertIn('expenses', response.context)
        self.assertEqual(len(response.context['expenses']), 1)
        
        # Test filtrowania po dacie
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(f"{reverse('reports:expense_report')}?start_date={start_date}&end_date={end_date}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 1)

    def test_consumption_report_view(self):
        """Test widoku raportu zużycia"""
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/consumption_report.html')
        self.assertIn('consumptions', response.context)
        self.assertEqual(len(response.context['consumptions']), 1)
        
        # Test filtrowania po produkcie
        response = self.client.get(f"{reverse('reports:consumption_report')}?product={self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 1)

    def test_wastage_report_view(self):
        """Test widoku raportu marnowania"""
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/wastage_report.html')
        self.assertIn('wastages', response.context)
        self.assertEqual(len(response.context['wastages']), 1)
        
        # Test filtrowania po przyczynie
        response = self.client.get(f"{reverse('reports:wastage_report')}?reason=Przeterminowany")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 1)

    def test_expense_trends_api(self):
        """Test API trendów wydatków"""
        response = self.client.get(reverse('reports:expense_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_consumption_trends_api(self):
        """Test API trendów zużycia"""
        response = self.client.get(reverse('reports:consumption_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_wastage_trends_api(self):
        """Test API trendów marnowania"""
        response = self.client.get(reverse('reports:wastage_trends_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_export_expense_csv(self):
        """Test eksportu wydatków do CSV"""
        response = self.client.get(reverse('reports:export_expense_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_expense_pdf(self):
        """Test eksportu wydatków do PDF"""
        response = self.client.get(reverse('reports:export_expense_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_consumption_csv(self):
        """Test eksportu zużycia do CSV"""
        response = self.client.get(reverse('reports:export_consumption_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_consumption_pdf(self):
        """Test eksportu zużycia do PDF"""
        response = self.client.get(reverse('reports:export_consumption_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_wastage_csv(self):
        """Test eksportu marnowania do CSV"""
        response = self.client.get(reverse('reports:export_wastage_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_wastage_pdf(self):
        """Test eksportu marnowania do PDF"""
        response = self.client.get(reverse('reports:export_wastage_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_unauthorized_access(self):
        """Test dostępu bez autoryzacji"""
        self.client.logout()
        
        # Test dostępu do dashboardu
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do formularza dodawania zużycia
        response = self.client.get(reverse('reports:add_consumption'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do formularza dodawania wydatku
        response = self.client.get(reverse('reports:add_expense'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do formularza dodawania marnowania
        response = self.client.get(reverse('reports:add_wastage'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do raportu wydatków
        response = self.client.get(reverse('reports:expense_report'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do raportu zużycia
        response = self.client.get(reverse('reports:consumption_report'))
        self.assertEqual(response.status_code, 302)
        
        # Test dostępu do raportu marnowania
        response = self.client.get(reverse('reports:wastage_report'))
        self.assertEqual(response.status_code, 302)

    def test_export_views(self):
        """Test widoków eksportu"""
        # Test eksportu CSV
        response = self.client.get(reverse('reports:export_expenses_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        response = self.client.get(reverse('reports:export_consumption_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        response = self.client.get(reverse('reports:export_wastage_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Test eksportu PDF
        response = self.client.get(reverse('reports:export_expenses_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        response = self.client.get(reverse('reports:export_consumption_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        response = self.client.get(reverse('reports:export_wastage_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

class ReportsFilteringAndErrorTests(TestCase):
    def setUp(self):
        # Tworzenie użytkownika
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Tworzenie kategorii
        self.category1 = Category.objects.create(
            name='Test Category 1',
            description='Test Description 1'
        )
        self.category2 = Category.objects.create(
            name='Test Category 2',
            description='Test Description 2'
        )
        
        # Tworzenie produktów
        self.product1 = Product.objects.create(
            name='Test Product 1',
            category=self.category1,
            unit='szt',
            barcode='123456789'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category2,
            unit='kg',
            barcode='987654321'
        )
        
        # Tworzenie list zakupów
        self.shopping_list1 = ShoppingList.objects.create(
            name='Test List 1',
            user=self.user
        )
        self.shopping_list2 = ShoppingList.objects.create(
            name='Test List 2',
            user=self.user
        )
        
        # Tworzenie przykładowych danych z różnymi datami
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        # Zużycie produktów
        self.consumption1 = ProductConsumption.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2.5,
            unit='szt',
            consumption_date=today
        )
        self.consumption2 = ProductConsumption.objects.create(
            user=self.user,
            product=self.product2,
            quantity=1.5,
            unit='kg',
            consumption_date=yesterday
        )
        self.consumption3 = ProductConsumption.objects.create(
            user=self.user,
            product=self.product1,
            quantity=3.0,
            unit='szt',
            consumption_date=last_week
        )
        
        # Wydatki
        self.expense1 = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list1,
            total_amount=100.50,
            shopping_date=today
        )
        self.expense2 = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list2,
            total_amount=200.75,
            shopping_date=yesterday
        )
        self.expense3 = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list1,
            total_amount=150.25,
            shopping_date=last_week
        )
        
        # Marnowanie
        self.wastage1 = ProductWastage.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1.0,
            unit='szt',
            wastage_date=today,
            reason='Przeterminowany'
        )
        self.wastage2 = ProductWastage.objects.create(
            user=self.user,
            product=self.product2,
            quantity=0.5,
            unit='kg',
            wastage_date=yesterday,
            reason='Uszkodzony'
        )
        self.wastage3 = ProductWastage.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2.0,
            unit='szt',
            wastage_date=last_week,
            reason='Zepsuty'
        )
        
        # Logowanie użytkownika
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_expense_report_filtering(self):
        """Test różnych scenariuszy filtrowania raportu wydatków"""
        # Filtrowanie po dacie
        start_date = (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(f"{reverse('reports:expense_report')}?start_date={start_date}&end_date={end_date}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 2)
        
        # Filtrowanie po liście zakupów
        response = self.client.get(f"{reverse('reports:expense_report')}?shopping_list={self.shopping_list1.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 2)
        
        # Filtrowanie po zakresie kwot
        response = self.client.get(f"{reverse('reports:expense_report')}?min_amount=150&max_amount=200")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 2)
        
        # Kombinacja filtrów
        response = self.client.get(
            f"{reverse('reports:expense_report')}?"
            f"start_date={start_date}&end_date={end_date}&"
            f"shopping_list={self.shopping_list1.id}&"
            f"min_amount=100&max_amount=200"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 1)

    def test_consumption_report_filtering(self):
        """Test różnych scenariuszy filtrowania raportu zużycia"""
        # Filtrowanie po dacie
        start_date = (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(f"{reverse('reports:consumption_report')}?start_date={start_date}&end_date={end_date}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 2)
        
        # Filtrowanie po produkcie
        response = self.client.get(f"{reverse('reports:consumption_report')}?product={self.product1.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 2)
        
        # Filtrowanie po kategorii
        response = self.client.get(f"{reverse('reports:consumption_report')}?category={self.category1.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 2)
        
        # Filtrowanie po zakresie ilości
        response = self.client.get(f"{reverse('reports:consumption_report')}?min_quantity=2&max_quantity=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 2)
        
        # Kombinacja filtrów
        response = self.client.get(
            f"{reverse('reports:consumption_report')}?"
            f"start_date={start_date}&end_date={end_date}&"
            f"product={self.product1.id}&"
            f"min_quantity=2&max_quantity=3"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 1)

    def test_wastage_report_filtering(self):
        """Test różnych scenariuszy filtrowania raportu marnowania"""
        # Filtrowanie po dacie
        start_date = (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(f"{reverse('reports:wastage_report')}?start_date={start_date}&end_date={end_date}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 2)
        
        # Filtrowanie po produkcie
        response = self.client.get(f"{reverse('reports:wastage_report')}?product={self.product1.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 2)
        
        # Filtrowanie po przyczynie
        response = self.client.get(f"{reverse('reports:wastage_report')}?reason=Przeterminowany")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 1)
        
        # Filtrowanie po zakresie ilości
        response = self.client.get(f"{reverse('reports:wastage_report')}?min_quantity=0.5&max_quantity=1.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 2)
        
        # Kombinacja filtrów
        response = self.client.get(
            f"{reverse('reports:wastage_report')}?"
            f"start_date={start_date}&end_date={end_date}&"
            f"product={self.product1.id}&"
            f"reason=Przeterminowany"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 1)

    def test_error_handling(self):
        """Test obsługi błędów w widokach"""
        # Test nieprawidłowych dat
        response = self.client.get(
            f"{reverse('reports:expense_report')}?"
            f"start_date=invalid_date&end_date=2024-13-45"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 3)  # Powinno zwrócić wszystkie wydatki
        
        # Test nieprawidłowych wartości numerycznych
        response = self.client.get(
            f"{reverse('reports:consumption_report')}?"
            f"min_quantity=abc&max_quantity=xyz"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 3)  # Powinno zwrócić wszystkie zużycia
        
        # Test nieprawidłowego ID produktu
        response = self.client.get(f"{reverse('reports:wastage_report')}?product=999999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 0)  # Powinno zwrócić pustą listę
        
        # Test nieprawidłowego ID kategorii
        response = self.client.get(f"{reverse('reports:consumption_report')}?category=999999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 0)  # Powinno zwrócić pustą listę
        
        # Test nieprawidłowego ID listy zakupów
        response = self.client.get(f"{reverse('reports:expense_report')}?shopping_list=999999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 0)  # Powinno zwrócić pustą listę

    def test_edge_cases(self):
        """Test przypadków brzegowych"""
        # Test pustych filtrów
        response = self.client.get(f"{reverse('reports:expense_report')}?start_date=&end_date=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 3)
        
        # Test przyszłych dat
        future_date = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(f"{reverse('reports:consumption_report')}?start_date={future_date}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 0)
        
        # Test ujemnych wartości
        response = self.client.get(f"{reverse('reports:wastage_report')}?min_quantity=-1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wastages']), 3)  # Powinno zignorować ujemną wartość
        
        # Test bardzo dużych wartości
        response = self.client.get(f"{reverse('reports:expense_report')}?max_amount=999999999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['expenses']), 3)
        
        # Test bardzo małych wartości
        response = self.client.get(f"{reverse('reports:consumption_report')}?min_quantity=0.000001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consumptions']), 3) 
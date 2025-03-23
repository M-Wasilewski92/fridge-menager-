from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList
from .models import ProductConsumption, ShoppingExpense, ProductWastage
from .forms import ProductConsumptionForm, ShoppingExpenseForm, ProductWastageForm

User = get_user_model()

class ProductConsumptionFormTests(TestCase):
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

    def test_valid_form(self):
        """Test poprawnego formularza"""
        form_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_quantity(self):
        """Test ujemnej ilości"""
        form_data = {
            'product': self.product.id,
            'quantity': -1,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_empty_unit(self):
        """Test pustej jednostki"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': '',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit', form.errors)

    def test_future_date(self):
        """Test przyszłej daty"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': 'szt',
            'consumption_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('consumption_date', form.errors)

    def test_invalid_unit(self):
        """Test nieprawidłowej jednostki"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': 'invalid_unit',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit', form.errors)

    def test_unit_mismatch(self):
        """Test niezgodności jednostki z produktem"""
        # Zmiana jednostki produktu
        self.product.unit = 'kg'
        self.product.save()
        
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit', form.errors)

class ShoppingExpenseFormTests(TestCase):
    def setUp(self):
        # Tworzenie użytkownika
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Tworzenie listy zakupów
        self.shopping_list = ShoppingList.objects.create(
            name='Test List',
            user=self.user
        )

    def test_valid_form(self):
        """Test poprawnego formularza"""
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_amount(self):
        """Test ujemnej kwoty"""
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': -100,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('total_amount', form.errors)

    def test_future_date(self):
        """Test przyszłej daty"""
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100,
            'shopping_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('shopping_date', form.errors)

class ProductWastageFormTests(TestCase):
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

    def test_valid_form(self):
        """Test poprawnego formularza"""
        form_data = {
            'product': self.product.id,
            'quantity': 1.0,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Przeterminowany'
        }
        form = ProductWastageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_quantity(self):
        """Test ujemnej ilości"""
        form_data = {
            'product': self.product.id,
            'quantity': -1,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Test'
        }
        form = ProductWastageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_empty_reason(self):
        """Test pustej przyczyny"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': ''
        }
        form = ProductWastageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('reason', form.errors)

    def test_future_date(self):
        """Test przyszłej daty"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'unit': 'szt',
            'wastage_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'reason': 'Test'
        }
        form = ProductWastageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('wastage_date', form.errors)

class ReportsFormsTests(TestCase):
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

    def test_product_consumption_form_valid(self):
        """Test poprawnego formularza zużycia produktu"""
        form_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_consumption_form_invalid(self):
        """Test niepoprawnego formularza zużycia produktu"""
        # Test pustego formularza
        form = ProductConsumptionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('product', form.errors)
        self.assertIn('quantity', form.errors)
        self.assertIn('unit', form.errors)
        self.assertIn('consumption_date', form.errors)
        
        # Test nieprawidłowej ilości
        form_data = {
            'product': self.product.id,
            'quantity': -1,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        
        # Test nieprawidłowej daty
        form_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': 'invalid-date'
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('consumption_date', form.errors)

    def test_shopping_expense_form_valid(self):
        """Test poprawnego formularza wydatków"""
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_shopping_expense_form_invalid(self):
        """Test niepoprawnego formularza wydatków"""
        # Test pustego formularza
        form = ShoppingExpenseForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('shopping_list', form.errors)
        self.assertIn('total_amount', form.errors)
        self.assertIn('shopping_date', form.errors)
        
        # Test nieprawidłowej kwoty
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': -100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('total_amount', form.errors)
        
        # Test nieprawidłowej daty
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100.50,
            'shopping_date': 'invalid-date'
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('shopping_date', form.errors)

    def test_product_wastage_form_valid(self):
        """Test poprawnego formularza marnowania"""
        form_data = {
            'product': self.product.id,
            'quantity': 1.0,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Przeterminowany'
        }
        form = ProductWastageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_wastage_form_invalid(self):
        """Test niepoprawnego formularza marnowania"""
        # Test pustego formularza
        form = ProductWastageForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('product', form.errors)
        self.assertIn('quantity', form.errors)
        self.assertIn('unit', form.errors)
        self.assertIn('wastage_date', form.errors)
        self.assertIn('reason', form.errors)
        
        # Test nieprawidłowej ilości
        form_data = {
            'product': self.product.id,
            'quantity': -1,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Przeterminowany'
        }
        form = ProductWastageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        
        # Test nieprawidłowej daty
        form_data = {
            'product': self.product.id,
            'quantity': 1.0,
            'unit': 'szt',
            'wastage_date': 'invalid-date',
            'reason': 'Przeterminowany'
        }
        form = ProductWastageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('wastage_date', form.errors)

    def test_form_save(self):
        """Test zapisywania formularzy"""
        # Test zapisywania zużycia
        form_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'szt',
            'consumption_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ProductConsumptionForm(data=form_data)
        self.assertTrue(form.is_valid())
        consumption = form.save(commit=False)
        consumption.user = self.user
        consumption.save()
        self.assertEqual(ProductConsumption.objects.count(), 1)
        
        # Test zapisywania wydatku
        form_data = {
            'shopping_list': self.shopping_list.id,
            'total_amount': 100.50,
            'shopping_date': timezone.now().strftime('%Y-%m-%d')
        }
        form = ShoppingExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())
        expense = form.save(commit=False)
        expense.user = self.user
        expense.save()
        self.assertEqual(ShoppingExpense.objects.count(), 1)
        
        # Test zapisywania marnowania
        form_data = {
            'product': self.product.id,
            'quantity': 1.0,
            'unit': 'szt',
            'wastage_date': timezone.now().strftime('%Y-%m-%d'),
            'reason': 'Przeterminowany'
        }
        form = ProductWastageForm(data=form_data)
        self.assertTrue(form.is_valid())
        wastage = form.save(commit=False)
        wastage.user = self.user
        wastage.save()
        self.assertEqual(ProductWastage.objects.count(), 1) 
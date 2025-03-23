from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from products.models import Product, Category
from shopping_lists.models import ShoppingList, ShoppingListItem
from .models import ProductConsumption, ShoppingExpense, ProductWastage

User = get_user_model()

class ProductConsumptionModelTests(TestCase):
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

    def test_create_consumption(self):
        """Test tworzenia zużycia produktu"""
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        self.assertEqual(consumption.quantity, 2.5)
        self.assertEqual(consumption.unit, 'szt')
        self.assertEqual(consumption.product, self.product)
        self.assertEqual(consumption.user, self.user)

    def test_negative_quantity(self):
        """Test ujemnej ilości"""
        with self.assertRaises(ValidationError):
            consumption = ProductConsumption(
                user=self.user,
                product=self.product,
                quantity=-1,
                unit='szt',
                consumption_date=timezone.now()
            )
            consumption.full_clean()

    def test_future_date(self):
        """Test przyszłej daty"""
        with self.assertRaises(ValidationError):
            consumption = ProductConsumption(
                user=self.user,
                product=self.product,
                quantity=1,
                unit='szt',
                consumption_date=timezone.now() + timedelta(days=1)
            )
            consumption.full_clean()

    def test_unit_mismatch(self):
        """Test niezgodności jednostki z produktem"""
        # Zmiana jednostki produktu
        self.product.unit = 'kg'
        self.product.save()
        
        with self.assertRaises(ValidationError):
            consumption = ProductConsumption(
                user=self.user,
                product=self.product,
                quantity=1,
                unit='szt',
                consumption_date=timezone.now()
            )
            consumption.full_clean()

class ShoppingExpenseModelTests(TestCase):
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

    def test_create_expense(self):
        """Test tworzenia wydatku"""
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        self.assertEqual(expense.total_amount, 100.50)
        self.assertEqual(expense.shopping_list, self.shopping_list)
        self.assertEqual(expense.user, self.user)

    def test_negative_amount(self):
        """Test ujemnej kwoty"""
        with self.assertRaises(ValidationError):
            expense = ShoppingExpense(
                user=self.user,
                shopping_list=self.shopping_list,
                total_amount=-100,
                shopping_date=timezone.now()
            )
            expense.full_clean()

    def test_future_date(self):
        """Test przyszłej daty"""
        with self.assertRaises(ValidationError):
            expense = ShoppingExpense(
                user=self.user,
                shopping_list=self.shopping_list,
                total_amount=100,
                shopping_date=timezone.now() + timedelta(days=1)
            )
            expense.full_clean()

class ProductWastageModelTests(TestCase):
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

    def test_create_wastage(self):
        """Test tworzenia marnowania"""
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        self.assertEqual(wastage.quantity, 1.0)
        self.assertEqual(wastage.unit, 'szt')
        self.assertEqual(wastage.product, self.product)
        self.assertEqual(wastage.user, self.user)
        self.assertEqual(wastage.reason, 'Przeterminowany')

    def test_negative_quantity(self):
        """Test ujemnej ilości"""
        with self.assertRaises(ValidationError):
            wastage = ProductWastage(
                user=self.user,
                product=self.product,
                quantity=-1,
                unit='szt',
                wastage_date=timezone.now(),
                reason='Test'
            )
            wastage.full_clean()

    def test_empty_reason(self):
        """Test pustej przyczyny"""
        with self.assertRaises(ValidationError):
            wastage = ProductWastage(
                user=self.user,
                product=self.product,
                quantity=1,
                unit='szt',
                wastage_date=timezone.now(),
                reason=''
            )
            wastage.full_clean()

    def test_future_date(self):
        """Test przyszłej daty"""
        with self.assertRaises(ValidationError):
            wastage = ProductWastage(
                user=self.user,
                product=self.product,
                quantity=1,
                unit='szt',
                wastage_date=timezone.now() + timedelta(days=1),
                reason='Test'
            )
            wastage.full_clean()

    def test_unit_mismatch(self):
        """Test niezgodności jednostki z produktem"""
        # Zmiana jednostki produktu
        self.product.unit = 'kg'
        self.product.save()
        
        with self.assertRaises(ValidationError):
            wastage = ProductWastage(
                user=self.user,
                product=self.product,
                quantity=1,
                unit='szt',
                wastage_date=timezone.now(),
                reason='Test'
            )
            wastage.full_clean()

class ModelRelationsTests(TestCase):
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

    def test_product_consumption_relations(self):
        """Test relacji dla zużycia produktu"""
        # Tworzenie zużycia
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Sprawdzanie relacji z użytkownikiem
        self.assertEqual(consumption.user, self.user)
        self.assertIn(consumption, self.user.productconsumption_set.all())
        
        # Sprawdzanie relacji z produktem
        self.assertEqual(consumption.product, self.product)
        self.assertIn(consumption, self.product.productconsumption_set.all())
        
        # Sprawdzanie relacji z kategorią przez produkt
        self.assertEqual(consumption.product.category, self.category)

    def test_shopping_expense_relations(self):
        """Test relacji dla wydatków"""
        # Tworzenie wydatku
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        # Sprawdzanie relacji z użytkownikiem
        self.assertEqual(expense.user, self.user)
        self.assertIn(expense, self.user.shoppingexpense_set.all())
        
        # Sprawdzanie relacji z listą zakupów
        self.assertEqual(expense.shopping_list, self.shopping_list)
        self.assertIn(expense, self.shopping_list.shoppingexpense_set.all())
        
        # Sprawdzanie relacji z użytkownikiem przez listę zakupów
        self.assertEqual(expense.shopping_list.user, self.user)

    def test_product_wastage_relations(self):
        """Test relacji dla marnowania produktu"""
        # Tworzenie marnowania
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        # Sprawdzanie relacji z użytkownikiem
        self.assertEqual(wastage.user, self.user)
        self.assertIn(wastage, self.user.productwastage_set.all())
        
        # Sprawdzanie relacji z produktem
        self.assertEqual(wastage.product, self.product)
        self.assertIn(wastage, self.product.productwastage_set.all())
        
        # Sprawdzanie relacji z kategorią przez produkt
        self.assertEqual(wastage.product.category, self.category)

    def test_cascade_delete(self):
        """Test kaskadowego usuwania"""
        # Tworzenie zużycia
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Tworzenie wydatku
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        # Tworzenie marnowania
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        # Usuwanie użytkownika
        self.user.delete()
        
        # Sprawdzanie czy powiązane obiekty zostały usunięte
        self.assertEqual(ProductConsumption.objects.count(), 0)
        self.assertEqual(ShoppingExpense.objects.count(), 0)
        self.assertEqual(ProductWastage.objects.count(), 0)

    def test_user_data_isolation(self):
        """Test izolacji danych użytkowników"""
        # Tworzenie drugiego użytkownika
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # Tworzenie produktu dla drugiego użytkownika
        product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            unit='szt',
            barcode='987654321'
        )
        
        # Tworzenie zużycia dla pierwszego użytkownika
        consumption1 = ProductConsumption.objects.create(
            user=self.user,
            product=self.product,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Tworzenie zużycia dla drugiego użytkownika
        consumption2 = ProductConsumption.objects.create(
            user=user2,
            product=product2,
            quantity=1.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        # Sprawdzanie izolacji danych
        self.assertEqual(self.user.productconsumption_set.count(), 1)
        self.assertEqual(user2.productconsumption_set.count(), 1)
        self.assertNotIn(consumption2, self.user.productconsumption_set.all())
        self.assertNotIn(consumption1, user2.productconsumption_set.all())

class ExtendedModelRelationsTests(TestCase):
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
        
        # Tworzenie pozycji na listach zakupów
        self.list_item1 = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list1,
            product=self.product1,
            quantity=2,
            unit='szt'
        )
        self.list_item2 = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list2,
            product=self.product2,
            quantity=1.5,
            unit='kg'
        )

    def test_category_product_relations(self):
        """Test relacji między kategoriami a produktami"""
        # Sprawdzanie relacji kategorii z produktami
        self.assertEqual(self.category1.product_set.count(), 1)
        self.assertEqual(self.category2.product_set.count(), 1)
        self.assertIn(self.product1, self.category1.product_set.all())
        self.assertIn(self.product2, self.category2.product_set.all())
        
        # Sprawdzanie relacji produktów z kategoriami
        self.assertEqual(self.product1.category, self.category1)
        self.assertEqual(self.product2.category, self.category2)
        
        # Sprawdzanie kaskadowego usuwania
        self.category1.delete()
        self.assertEqual(Product.objects.filter(category=self.category1).count(), 0)

    def test_shopping_list_product_relations(self):
        """Test relacji między listami zakupów a produktami"""
        # Sprawdzanie relacji list z pozycjami
        self.assertEqual(self.shopping_list1.shoppinglistitem_set.count(), 1)
        self.assertEqual(self.shopping_list2.shoppinglistitem_set.count(), 1)
        self.assertIn(self.list_item1, self.shopping_list1.shoppinglistitem_set.all())
        self.assertIn(self.list_item2, self.shopping_list2.shoppinglistitem_set.all())
        
        # Sprawdzanie relacji pozycji z produktami
        self.assertEqual(self.list_item1.product, self.product1)
        self.assertEqual(self.list_item2.product, self.product2)
        
        # Sprawdzanie kaskadowego usuwania
        self.shopping_list1.delete()
        self.assertEqual(ShoppingListItem.objects.filter(shopping_list=self.shopping_list1).count(), 0)

    def test_report_type_relations(self):
        """Test relacji między różnymi typami raportów"""
        # Tworzenie różnych typów raportów dla tego samego produktu
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list1,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        # Sprawdzanie relacji między raportami a produktem
        self.assertEqual(self.product1.productconsumption_set.count(), 1)
        self.assertEqual(self.product1.productwastage_set.count(), 1)
        self.assertEqual(self.shopping_list1.shoppingexpense_set.count(), 1)
        
        # Sprawdzanie relacji między raportami a użytkownikiem
        self.assertEqual(self.user.productconsumption_set.count(), 1)
        self.assertEqual(self.user.productwastage_set.count(), 1)
        self.assertEqual(self.user.shoppingexpense_set.count(), 1)

    def test_cross_app_relations(self):
        """Test relacji między różnymi aplikacjami"""
        # Sprawdzanie relacji między aplikacją reports a products
        self.assertEqual(self.product1.productconsumption_set.count(), 0)
        self.assertEqual(self.product1.productwastage_set.count(), 0)
        
        # Sprawdzanie relacji między aplikacją reports a shopping_lists
        self.assertEqual(self.shopping_list1.shoppingexpense_set.count(), 0)
        
        # Tworzenie raportów
        consumption = ProductConsumption.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2.5,
            unit='szt',
            consumption_date=timezone.now()
        )
        
        wastage = ProductWastage.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1.0,
            unit='szt',
            wastage_date=timezone.now(),
            reason='Przeterminowany'
        )
        
        expense = ShoppingExpense.objects.create(
            user=self.user,
            shopping_list=self.shopping_list1,
            total_amount=100.50,
            shopping_date=timezone.now()
        )
        
        # Sprawdzanie relacji po utworzeniu raportów
        self.assertEqual(self.product1.productconsumption_set.count(), 1)
        self.assertEqual(self.product1.productwastage_set.count(), 1)
        self.assertEqual(self.shopping_list1.shoppingexpense_set.count(), 1)
        
        # Sprawdzanie relacji między aplikacjami przez użytkownika
        self.assertEqual(self.user.product_set.count(), 0)  # Produkty nie należą do użytkownika
        self.assertEqual(self.user.shoppinglist_set.count(), 2)  # Listy zakupów należą do użytkownika
        self.assertEqual(self.user.productconsumption_set.count(), 1)
        self.assertEqual(self.user.productwastage_set.count(), 1)
        self.assertEqual(self.user.shoppingexpense_set.count(), 1) 
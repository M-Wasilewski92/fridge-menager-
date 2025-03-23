from django.db import models
from django.conf import settings
from products.models import Product, Category
from django.utils import timezone

class ProductConsumption(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    consumption_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-consumption_date']
        verbose_name = 'Zużycie produktu'
        verbose_name_plural = 'Zużycie produktów'

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit} ({self.consumption_date})"

class ShoppingExpense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shopping_list = models.ForeignKey('shopping_list.ShoppingList', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shopping_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-shopping_date']
        verbose_name = 'Wydatek na zakupy'
        verbose_name_plural = 'Wydatki na zakupy'

    def __str__(self):
        return f"Zakupy {self.shopping_date} - {self.total_amount} zł"

class CategoryExpense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'category', 'month']
        ordering = ['-month']

    def __str__(self):
        return f"{self.category.name} - {self.month.strftime('%B %Y')} - {self.total_amount} zł"

class ProductWastage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    wastage_date = models.DateField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-wastage_date']
        verbose_name = 'Marnowanie produktu'
        verbose_name_plural = 'Marnowanie produktów'

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit} ({self.wastage_date})"

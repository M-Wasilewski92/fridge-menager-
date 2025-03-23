from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import ProductConsumption, ShoppingExpense, ProductWastage

class ProductConsumptionForm(forms.ModelForm):
    class Meta:
        model = ProductConsumption
        fields = ['product', 'quantity', 'unit', 'consumption_date']
        widgets = {
            'consumption_date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='form-group col-md-6 mb-0'),
                Column('quantity', css_class='form-group col-md-3 mb-0'),
                Column('unit', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('consumption_date', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Dodaj zużycie')
        )

class ShoppingExpenseForm(forms.ModelForm):
    class Meta:
        model = ShoppingExpense
        fields = ['shopping_list', 'total_amount', 'shopping_date']
        widgets = {
            'shopping_date': forms.DateInput(attrs={'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('shopping_list', css_class='form-group col-md-6 mb-0'),
                Column('total_amount', css_class='form-group col-md-3 mb-0'),
                Column('shopping_date', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Dodaj wydatek')
        )

class ProductWastageForm(forms.ModelForm):
    class Meta:
        model = ProductWastage
        fields = ['product', 'quantity', 'unit', 'wastage_date', 'reason']
        widgets = {
            'wastage_date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='form-group col-md-6 mb-0'),
                Column('quantity', css_class='form-group col-md-3 mb-0'),
                Column('unit', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('wastage_date', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('reason', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Dodaj marnowanie')
        ) 
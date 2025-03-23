from django import forms
from .models import ShoppingList, ShoppingListItem
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            Submit('submit', 'Zapisz listę', css_class='btn-primary mt-3')
        )

class ShoppingListItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingListItem
        fields = ['product', 'quantity', 'unit']
        widgets = {
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
            Submit('submit', 'Dodaj produkt', css_class='btn-primary mt-3')
        ) 
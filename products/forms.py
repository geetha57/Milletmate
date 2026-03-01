from django import forms
from .models import MilletProduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = MilletProduct
        fields = ['millet_type', 'quantity', 'unit', 'price', 'location', 'harvest_date', 'image', 'description']
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }
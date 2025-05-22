from django import forms
from .models import Product, Category, Currency, City

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'description', 'image', 'price', 'currency', 'city']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'
        
        self.fields['city'].queryset = City.objects.all().order_by('name')
        self.fields['city'].empty_label = None
        first = self.fields['city'].queryset.first()
        if first is not None:
            self.fields['city'].initial = first.pk
        
        self.fields['currency'].queryset = Currency.objects.all().order_by('order')
        self.fields['currency'].empty_label = None
        first =self.fields['currency'].queryset.first()
        if first is not None:
            self.fields['currency'].initial = first.pk


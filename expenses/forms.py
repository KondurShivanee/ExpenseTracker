from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """Form for creating and editing expenses."""

    class Meta:
        model = Expense
        fields = ['amount', 'description', 'category', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What did you spend on?',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""

    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name',
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., bi-cart, bi-house',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
            }),
        }


class ExpenseFilterForm(forms.Form):
    """Form for filtering expenses."""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )

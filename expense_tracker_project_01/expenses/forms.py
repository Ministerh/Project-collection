from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'description']
        widgets = {
            "date": forms.DateInput(attrs={'type': 'date'}, format='%m/%d/%Y'),
        }

    def clean_category(self):
        return self.cleaned_data['category'].strip().lower()
from django import forms
from .models import Branch, CustomUser
from django.contrib.auth.forms import UserCreationForm

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'location', 'region', 'code', 'status', 'daily_target', 'daily_page_target']
        labels = {
            'daily_target': 'ስካን የተደረጉ የፋይል ብዛት የቀን እቅድ',
            'daily_page_target': 'ስካን የተደረገ የገፅ ብዛት የቀን እቅድ',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'daily_target': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_page_target': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role', 'branch', 'status')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

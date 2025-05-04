# account/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
    }))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'phone_number', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
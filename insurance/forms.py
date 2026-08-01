from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Policy, Claim, Document


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'state', 'zip_code', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['policy_type', 'start_date', 'end_date', 'premium_amount', 'coverage_amount']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['claim_type', 'description', 'incident_date', 'claim_amount']
        widgets = {
            'incident_date': forms.DateInput(attrs={'type': 'date'}),
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'document_type']

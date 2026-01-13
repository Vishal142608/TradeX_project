from django import forms
from django.contrib.auth.models import User
from .models import Profile

class TradeXRegistrationForm(forms.Form):
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )
    phone_number = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter mobile number',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create password',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Normalize: digits only
        normalized_phone = ''.join(filter(str.isdigit, str(phone)))
        if len(normalized_phone) < 10 or len(normalized_phone) > 13:
            raise forms.ValidationError("Phone number must be between 10 and 13 digits.")
        if Profile.objects.filter(phone_number=normalized_phone).exists():
            raise forms.ValidationError("Phone number already registered.")
        return normalized_phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class TradeXLoginForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter mobile number',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )

class BuyStockForm(forms.Form):
    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'How many shares?',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-2xl font-black focus:outline-none focus:border-groww transition',
            'id': 'quantity'
        })
    )

class SellStockForm(forms.Form):
    quantity = forms.IntegerField(
        label="Quantity to Sell",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Units to sell',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-2xl font-black focus:outline-none focus:border-red-500 transition',
            'id': 'quantity'
        })
    )

class SIPForm(forms.Form):
    PLAN_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    amount = forms.DecimalField(
        label="Monthly Investment Amount",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'e.g. 5000',
            'class': 'w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition'
        })
    )
    frequency = forms.ChoiceField(
        choices=PLAN_CHOICES,
        label="Frequency",
        widget=forms.Select(attrs={
            'class': 'w-full bg-[#1a1c1e] border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-groww transition text-white'
        })
    )

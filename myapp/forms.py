from django import forms
from django.contrib.auth import get_user_model
from django import forms
from .models import Product, Settings
from django.core.exceptions import ValidationError
import os
from .models import Product, User, Profile, Review, Address
from django.contrib.auth.forms import UserCreationForm




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'brand', 'colors', 'description', 'image1', 'image2', 'image3', 'image4' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['colors'].help_text = "Enter colors as a comma-separated list (e.g., Red, Blue, Green)."





class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = get_user_model()  # Use the custom user model
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Full Name"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone"}))
    address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Address"}))
    country = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Country"}))
    image = forms.ImageField(required=False, help_text="Upload a profile photo (JPEG, PNG format).")  # Optional image field

    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'address', 'country', 'image']  # Include all relevant fields


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address  # Make sure to use your actual Address model
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'additional_phone_number',
            'address_line',
            'additional_information',
            'region',
            'city'
        ]

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  # Add Bootstrap class to each field


class NewsletterSubscriptionForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            "site_name",
            "logo",
            "contact_email",
            "contact_phone",
            "business_address",
            "currency",
            "enable_mpesa",
            "mpesa_api_key",
            "enable_paypal",
            "paypal_client_id",
            "paypal_client_secret",
            "enable_visa",
            "visa_api_key",
            "flat_shipping_rate",
            "enable_free_shipping",
            "free_shipping_threshold",
            "homepage_meta_title",
            "homepage_meta_description",
            "facebook_url",
            "instagram_url",
            "maintenance_mode",
            "maintenance_message",
        ]
        widgets = {
            # Add Visa-specific widgets
            "enable_visa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "visa_api_key": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Visa API key"}),
        
            "site_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter site name"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter contact email"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter contact phone"}),
            "business_address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter business address"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "enable_mpesa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mpesa_api_key": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter M-Pesa API key"}),
            "enable_paypal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "paypal_client_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter PayPal Client ID"}),
            "paypal_client_secret": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter PayPal Client Secret"}),
            "flat_shipping_rate": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter flat shipping rate"}),
            "enable_free_shipping": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "free_shipping_threshold": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter free shipping threshold"}),
            "homepage_meta_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter homepage meta title"}),
            "homepage_meta_description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter meta description"}),
            "facebook_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Enter Facebook URL"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Enter Instagram URL"}),
            "maintenance_mode": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "maintenance_message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter maintenance message"}),
        }


from django import forms
from django.contrib.auth import get_user_model
from django import forms
from .models import Product
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
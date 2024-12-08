from django import forms
from django.contrib.auth import get_user_model

from .models import Product, User, Profile, Review
from django.contrib.auth.forms import UserCreationForm


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'brand', 'colors', 'image']

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



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
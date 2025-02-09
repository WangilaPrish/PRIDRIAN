from datetime import timezone
from enum import unique
import os
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)  # Ensure this is defined
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Include username in required fields

    objects = CustomUserManager()

    def __str__(self):
        return self.email



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_photos", null=True, blank=True)  # Specify upload path for profile photos
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    verified = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.full_name} "


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Change to ForeignKey
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    additional_phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional
    address_line = models.TextField()
    additional_information = models.TextField(blank=True, null=True)  # Optional
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)  # You can add this to allow setting a default address

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def validate_image_extension(value):
    valid_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg', '.heif', '.raw'
    ]
    ext = os.path.splitext(value.name)[1].lower()  # Extract and normalize the file extension
    if ext not in valid_extensions:
        raise ValidationError(
            'File type not supported. Please upload an image file with one of the following extensions: '
            '.jpg, .jpeg, .png, .gif, .webp, .bmp, .tiff, .svg, .heif, .raw'
        )

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=200, null=True, blank=True)
    colors = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField()

    # Apply the validation function to the ImageFields
    image1 = models.ImageField(upload_to='products/', validators=[validate_image_extension], blank=True, null=True)
    image2 = models.ImageField(upload_to='products/', validators=[validate_image_extension], blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', validators=[validate_image_extension], blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', validators=[validate_image_extension], blank=True, null=True)

    def get_colors(self):
        return self.colors.split(",") if self.colors else []

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveIntegerField()  # Rating out of 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Now allows NULLs
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_color = models.CharField(max_length=50, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.user.username}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', related_name='wishlists')

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    mpesa_number = models.CharField(max_length=15)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # Ensure this line exists
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order {self.order.id}"


class Newsletter(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class Settings(models.Model):
    # General Settings
    site_name = models.CharField(max_length=255, default="PRIDRIAN Luxe")
    logo = models.ImageField(upload_to="settings/logos/", null=True, blank=True)
    contact_email = models.EmailField(max_length=255, default="info@pridrianluxe.com")
    contact_phone = models.CharField(max_length=15, default="070-020-0340")
    business_address = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=10, default="KES")

    # Payment Settings
    enable_mpesa = models.BooleanField(default=True)
    mpesa_api_key = models.CharField(max_length=255, null=True, blank=True)
    enable_paypal = models.BooleanField(default=False)
    paypal_client_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_client_secret = models.CharField(max_length=255, null=True, blank=True)
    enable_visa = models.BooleanField(default=False)  # Add this field
    visa_api_key = models.CharField(max_length=255, blank=True, null=True)  # Add this field


    # Shipping Settings
    flat_shipping_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    enable_free_shipping = models.BooleanField(default=False)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # SEO and Marketing
    homepage_meta_title = models.CharField(max_length=255, null=True, blank=True)
    homepage_meta_description = models.TextField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)

    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(default="We are currently performing maintenance. Please check back later.")

    # Other Settings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name
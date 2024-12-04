from django.db import models


class User(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.firstname



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=200, null=True, blank=True)
    colors = models.CharField(max_length=500, null=True, blank=True)

    def get_colors(self):
        return self.colors.split(",") if self.colors else []

    def __str__(self):
        return self.name


class CartItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    selected_color = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.product.price

class Newsletter(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email
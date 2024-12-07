from django.contrib import admin
from myapp.models import User, Product, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Profile)

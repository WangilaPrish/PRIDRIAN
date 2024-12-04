
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('shopandcart/', views.shopandcart, name='shopandcart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('shopp/', views.shopp, name='shopp'),

    path('shopsingle/', views.shopsingle, name='shopsingle'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('cart/', views.cart, name='cart'),
    path('addproduct/', views.addproduct, name='addproduct'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


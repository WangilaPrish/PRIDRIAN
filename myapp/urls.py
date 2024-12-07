
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('useradmin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('', views.shop, name='shop'),
    path('shopandcart/<int:product_id>/', views.shopandcart, name='shopandcart'),
    #path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('shopp/', views.shopp, name='shopp'),
    path('shopsingle/', views.shopsingle, name='shopsingle'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),

    path('logout/', views.logout, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('reviews/', views.reviews, name='reviews'),
    path('profile/update/', views.profile_update, name='profile'),
    path('update-quantity/<int:item_id>/', views.update_cart_quantity, name='update_quantity'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/<str:oid>/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('paymentsuccess/', views.paymentsuccess, name='paymentsuccess'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


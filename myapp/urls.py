
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

from myapp.views import profile, change_password, user_logout, featured_products, edit_product, view_buyer_profile, \
    order_history, delete_user, add_to_wishlist, remove_from_wishlist, wishlist, get_wishlist_items,  \
    add_address, edit

urlpatterns = [
    path('useradmin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('', views.featured_products, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('shopandcart/<int:product_id>/', views.shopandcart, name='shopandcart'),
    #path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('shopsingle/', views.shopsingle, name='shopsingle'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),

    path('logout/', views.logout, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('get-wishlist-items/', get_wishlist_items, name='get_wishlist_items'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('edit-product/<int:product_id>/', edit_product, name='edit_product'),
    path('reviews/<int:product_id>/', views.reviews, name='reviews'),
    path('profile/', profile, name='profile'),  # For viewing the profile
    path('edit/<int:pk>/', edit, name='edit'),
    path('addresses/', views.address, name='address'),
    path('addresses/add/', views.add_address, name='add_address'),

    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),

    path('profile/update/', profile, name='profile_update'),
    path('profile/change_password/', change_password, name='change_password'),  # For changing password
    path('admin/view-buyer-profiles/', views.profile, name='admin_buyer_profiles'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),


    path('logout/', user_logout, name='logout'),
    path('update-cart/', views.update_cart_quantity, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('stk/', views.stk, name='stk'),
    path('token/', views.token, name='token'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-history/<int:order_id>/', order_history, name='order_detail'),
    path('order-success/', views.order_success, name='order_success'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


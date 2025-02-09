from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

from myapp.views import (
    edit_settings, profile, change_password, user_logout, featured_products, edit_product,
    view_buyer_profile, order_history, delete_user, add_to_wishlist, remove_from_wishlist, view_settings,
    wishlist, get_wishlist_items, add_address, edit, admin_dashboard, delete_product,
    product_management,edit_settings, order_management, customer_management, edit_product)

urlpatterns = [
    # Admin Routes
    path('useradmin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/products/', product_management, name='product_management'),
    path('admin/products/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('admin/orders/', order_management, name='order_management'),
    path('admin/customers/', customer_management, name='customer_management'),
    path('admin/settings/', view_settings, name='view_settings'),
    path('admin/settings/edit/', edit_settings, name='edit_settings'),

    # User and Public Routes
    path('index/', views.index, name='index'),
    path('', views.featured_products, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('shopandcart/<int:product_id>/', views.shopandcart, name='shopandcart'),
    path('shopsingle/', views.shopsingle, name='shopsingle'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # Cart Routes
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),

    # Wishlist Routes
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('get-wishlist-items/', get_wishlist_items, name='get_wishlist_items'),

    # Address Routes
    path('addresses/', views.address, name='address'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:pk>/', edit, name='edit'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),

    # Profile Routes
    path('profile/', profile, name='profile'),
    path('profile/change_password/', change_password, name='change_password'),
    path('profile/update/', profile, name='profile_update'),

    # Admin Buyer Management
    path('admin/view-buyer-profiles/', view_buyer_profile, name='admin_buyer_profiles'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),

    # Product Management
    path('addproduct/', views.addproduct, name='addproduct'),
    path('edit-product/<int:product_id>/', edit_product, name='edit_product'),

    # Review Routes
    path('reviews/<int:product_id>/', views.reviews, name='reviews'),

    # Checkout and Payment
    path('checkout/', views.checkout, name='checkout'),
    path('stk/', views.stk, name='stk'),
    path('token/', views.token, name='token'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-history/<int:order_id>/', order_history, name='order_detail'),
    path('order-success/', views.order_success, name='order_success'),
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

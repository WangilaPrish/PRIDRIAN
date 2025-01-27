import requests
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from myapp.forms import ProductForm, ProfileForm, UserRegisterForm, ReviewForm, AddressForm
from myapp.models import User, Product, CartItem, Newsletter, Profile, Review, Order, OrderItem, Wishlist, Address
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import User
from requests.auth import HTTPBasicAuth
from myapp.credentials import MpesaAccessToken, LipanaMpesaPpassword

# Create your views here.
def user_login(request):
    if request.user.is_authenticated:
        return redirect("index")  # Redirect to the index page if already logged in

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Ensure the profile exists
            try:
                user.profile  # Try accessing the profile to ensure it exists
            except Profile.DoesNotExist:
                # If no profile exists, create one
                Profile.objects.create(user=user)

            # Log the user in
            login(request, user)
            next_url = request.GET.get("next", "index")  # Redirect to 'next' or index
            return redirect(next_url)
        else:
            # If authentication fails, check if the user exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.error(request, f"No account found for {email}. Please register.")

    return render(request, "registration/login.html")

def user_logout(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('registration:login')  # Ensure this points to your login page


def about(request):
    return render(request, 'about.html')



def contact(request):
    return render(request, 'contact.html')


def shopsingle(request):
    return render(request, 'shop-single.html')


@login_required
def profile(request):
    user = request.user
    # Get or create the user's default address
    address = Address.objects.filter(user=user, is_default=True).first()

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = AddressForm(instance=address)

    return render(request, 'profile.html', {'user': user, 'address': address, 'address_form': form})



def edit(request, pk):
    address = get_object_or_404(Address, pk=pk)  # Get the address instance by primary key (pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)  # Bind the form to the instance
        if form.is_valid():
            form.save()  # Save the updated address
            return redirect('address')  # Redirect to profile page after saving
    else:
        form = AddressForm(instance=address)  # Prepopulate the form with the current address details

    return render(request, 'edit.html', {'address_form': form})  # Pass the form as 'address_form' for the template


def address(request):
    addresses = Address.objects.filter(user=request.user)  # Assuming you have a ForeignKey to user
    return render(request, 'address.html', {'addresses': addresses})



# View to add a new address
@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Associate the address with the user
            address.save()

            # Optionally, set this address as the default if the user wants
            if request.POST.get('set_as_default'):
                # Set all other addresses for this user to not default
                Address.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True
                address.save()

            return redirect('address')  # Redirect to the address overview
    else:
        form = AddressForm()

    return render(request, 'add_address.html', {'form': form})

# View to edit an existing address


# View to delete an address
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('address')
    return render(request, 'confirm_delete.html', {'address': address})

# View to set an address as default
def set_default_address(request, address_id):
    # Get the address object, or return a 404 error if not found
    address = get_object_or_404(Address, id=address_id, user=request.user)

    # Set all other addresses to not default
    Address.objects.filter(user=request.user).update(is_default=False)

    # Set the selected address as default
    address.is_default = True
    address.save()

    # Redirect to the profile page after setting the default address
    return redirect('profile')  # Change 'profile' to match your URL name for the profile page

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def view_buyer_profile(request, user_id):
    # Get the user's profile using their user ID
    user_profile = get_object_or_404(User, id=user_id)

    # Render the profile template with the user's details
    return render(request, 'buyer_profile.html', {'profile': user_profile})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        raise PermissionDenied("You cannot delete your own account.")

    user.delete()
    messages.success(request, "User account has been deleted successfully.")
    return redirect('admin_buyer_profiles')  # Redirect to the admin buyer profiles page


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in after changing the password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect to profile or any other page
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {
        'form': form
    })


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            authenticated_user = authenticate(
                email=user.email, password=form.cleaned_data['password1']
            )
            if authenticated_user:
                login(request, authenticated_user)

                return redirect('index')  # Redirect to the home page or another page
            else:
                messages.error(request, "Unable to log in. Please try again.")
    else:
        form = UserRegisterForm()

    return render(request, "register.html", {"form": form})




def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('/index')

        # Validate the email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect('/index')

        # Proceed with saving the newsletter
        members = Newsletter(email=email)
        members.save()

        messages.success(request, "Successfully subscribed.")
        return redirect('/index')

    else:
        # Fetch all products that have at least one review
        featured_products = Product.objects.annotate(review_count=Count('reviews')).filter(review_count__gt=0)

        return render(request, 'index.html', {
            'featured_products': featured_products  # Pass the featured products to the template
        })


def shop(request):
    brand_name = request.GET.get('brand', '')  # Get the selected brand, default to an empty string
    sort_by = request.GET.get('sort_by', 'popularity')  # Default sort is by popularity

    # Filter by brand
    if brand_name:
        products = Product.objects.filter(brand__icontains=brand_name)
    else:
        products = Product.objects.all()

    # Sort products based on the selected criteria
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'arrival':
        products = products.order_by('-created_at')  # Assuming you have a created_at field
    else:
        products = products.annotate(review_count=Count('reviews')).order_by('-review_count')  # Default to sorting by popularity

    # Get distinct brands for the filter options
    brands = Product.objects.values_list('brand', flat=True).distinct()

    # Pass the selected brand and sorting option to the template
    context = {
        'products': products,
        'brands': brands,
        'selected_brand': brand_name,
        'selected_sort': sort_by
    }
    return render(request, 'shop.html', context)


def cart(request):
    cart_total = 0

    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']

        # Calculate the total amount in the cart
        for product_id, item in cart_data.items():
            cart_total += int(item['quantity']) * float(item['price'])

        return render(request, 'cart.html', {
            'cart_data': cart_data,
            'totalcartitems': len(cart_data),
            'cart_total': cart_total,
            'oid': None  # No order ID needed for cart view
        })
    else:
        return render(request, 'cart.html', {
            'cart_data': None,
            'totalcartitems': 0,
            'cart_total': cart_total,
            'oid': None
        })


def wishlist(request):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        wishlist_items = wishlist.products.all().order_by('id') if wishlist else []  # Order by 'id'

        # Set up pagination
        paginator = Paginator(wishlist_items, 10)  # Show 10 products per page
        page_number = request.GET.get('page')  # Get the page number from the URL
        page_obj = paginator.get_page(page_number)  # Get the products for the current page

        # Add stock status for each product in the page object
        for product in page_obj:
            product.is_out_of_stock = product.stock == 0

        # Get the total number of products in the wishlist
        total_products_count = len(wishlist_items)  # Use len() for a list

        return render(request, 'wishlist.html', {'page_obj': page_obj, 'total_products_count': total_products_count})  # Pass 'total_products_count'
    else:
        return render(request, 'wishlist.html', {'page_obj': None, 'total_products_count': 0})  # Pass 0 for unauthenticated users


def add_to_wishlist(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        wishlist.products.add(product)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def remove_from_wishlist(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            product = get_object_or_404(Product, id=product_id)
            wishlist.products.remove(product)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)



@login_required
def get_wishlist_items(request):
    # Assuming you have a Wishlist model related to the user
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    items = []
    for item in wishlist_items:
        items.append({
            'product': {
                'id': item.product.id,
                'name': item.product.name,
                'image': item.product.image.url,
                'price': item.product.price,
            }
        })

    return JsonResponse({'wishlist_items': items})

def shopandcart(request, product_id):
    # Fetch the specific product by its ID
    product = get_object_or_404(Product, id=product_id)

    # Fetch reviews for this product
    reviews = product.reviews.all()  # Ensure your Review model has a related_name='reviews'

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if the user has already submitted a review for this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                # Optionally update the existing review instead of creating a new one
                existing_review.rating = form.cleaned_data['rating']
                existing_review.content = form.cleaned_data['content']
                existing_review.save()
            else:
                # Create a new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
            return redirect('shopandcart', product_id=product.id)  # Redirect back to the product detail page
    else:
        form = ReviewForm()  # Initialize the review form for GET requests

    return render(request, 'shopandcart.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

def featured_products(request):
    # Fetch products that have reviews
    products_with_reviews = Product.objects.filter(reviews__isnull=False).distinct()

    return render(request, 'index.html', {'featured_products': products_with_reviews})

def is_admin(user):
    """Check if the user is an admin."""
    return user.is_superuser


@login_required  # Ensure the user is logged in
@user_passes_test(is_admin)  # Ensure the user is an admin
def addproduct(request):
    if not request.user.is_superuser:
        raise PermissionDenied  # Raise a 403 Forbidden error

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Include request.FILES to handle image files
        if form.is_valid():
            # Save the product
            product = form.save(commit=False)

            # Check if images are provided and assign them
            if 'image1' in request.FILES:
                product.image1 = request.FILES['image1']
            if 'image2' in request.FILES:
                product.image2 = request.FILES['image2']
            if 'image3' in request.FILES:
                product.image3 = request.FILES['image3']
            if 'image4' in request.FILES:
                product.image4 = request.FILES['image4']

            # Save the product with the images
            product.save()

            return redirect('shop')  # Redirect to the shop page after successful product creation
    else:
        form = ProductForm()

    return render(request, 'addproduct.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop')  # Redirect to shop or wherever you want
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})



@csrf_exempt  # Only for testing; avoid in production
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            print("Received data:", data)  # Debugging: Log the received data

            # Check if all required fields are present in the request
            required_fields = ['id', 'name', 'quantity', 'price', 'image', 'color']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'message': f'Missing required field: {field}'}, status=400)

            # Create the cart product structure
            cart_product = {
                str(data['id']): {
                    'name': data['name'],
                    'quantity': int(data['quantity']),
                    'price': float(data['price']),
                    'image': data['image'],
                    'product_id': data['id'],
                    'color': data['color'],  # Add color to the cart structure
                }
            }

            # Check if there's an existing cart in the session
            if 'cart_data_object' in request.session:
                cart_data = request.session['cart_data_object']

                if str(data['id']) in cart_data:
                    # Update quantity if the product already exists in the cart
                    cart_data[str(data['id'])]['quantity'] += int(data['quantity'])
                else:
                    # Add the new product to the cart
                    cart_data.update(cart_product)

                # Save the updated cart to the session
                request.session['cart_data_object'] = cart_data
            else:
                # Initialize a new cart with the product
                request.session['cart_data_object'] = cart_product

            # Debugging: Log the updated cart data
            print(f"Updated cart data: {request.session['cart_data_object']}")

            # Calculate the total number of items in the cart
            total_cart_items = sum(item['quantity'] for item in request.session['cart_data_object'].values())

            return JsonResponse({
                "success": True,
                "data": request.session['cart_data_object'],
                "totalcartitems": total_cart_items
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        # Check if the cart exists in the session
        if 'cart_data_object' in request.session:
            cart_data = request.session['cart_data_object']

            # Remove the item from the cart if it exists
            if str(item_id) in cart_data:
                del cart_data[str(item_id)]  # Remove the item by its ID

                # Update the session with the modified cart
                request.session['cart_data_object'] = cart_data

                # Return the updated cart data
                return JsonResponse({'status': 'success', 'cart': cart_data})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def update_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # Ensure the cart data exists in the session
        if 'cart_data_object' in request.session:
            cart_data = request.session['cart_data_object']

            if str(product_id) in cart_data:
                cart_data[str(product_id)]['quantity'] = int(quantity)  # Update quantity
                request.session['cart_data_object'] = cart_data  # Save back to session

                return JsonResponse({'status': 'success', 'cart_data': cart_data})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)

        return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def order_history(request):
    if request.user.is_superuser:
        # Admin sees all orders
        orders = Order.objects.all().order_by('-created_at')
    else:
        # Buyers see only their orders
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'order_history.html', {'orders': orders})



def get_cart_data(request):
    # Function to fetch the current cart data (items and total)
    cart_items = CartItem.objects.filter(user=request.user if request.user.is_authenticated else None)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return {'items': [{'id': item.id, 'name': item.product.name, 'price': item.product.price, 'quantity': item.quantity, 'image': item.product.image.url} for item in cart_items], 'total': total}


@login_required
def reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        product = get_object_or_404(Product, id=product_id)

        # Create a new review
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            content=content
        )

        # Redirect back to the product detail page
        return redirect('shopandcart', product_id=product_id)  # Adjust according to your URL


@login_required  # Only allow access to authenticated users
def checkout(request):
    # Initialize cart total and cart data
    cart_total = 0
    cart_data = {}

    # Retrieve cart data from the session if it exists
    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']
        # Calculate the total amount in the cart
        for product_id, item in cart_data.items():
            cart_total += int(item['quantity']) * float(item['price'])

    if request.method == 'POST':
        # Retrieve the M-Pesa number and total amount from the POST data
        mpesa_number = request.POST.get('mpesa_number')
        total_amount = cart_total + 0  # Add fixed shipping fee

        # Validate input
        if not mpesa_number:
            messages.error(request, "M-Pesa number is required.")
            return redirect('checkout')

        # Create the order
        order = Order.objects.create(
            user=request.user,  # Link order to the logged-in user
            total=total_amount,
            name=request.user.get_full_name(),
            phone=mpesa_number,  # Use the M-Pesa number as a temporary phone number
            county="N/A",  # Placeholder values since not collected
            town="N/A",    # Placeholder values since not collected
            mpesa_number=mpesa_number,
            status="Pending",  # Default status for new orders
        )

        # Create OrderItem for each product in the cart
        for product_id, item in cart_data.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=float(item['price']),
            )

        # Clear the cart data from the session after order placement
        del request.session['cart_data_object']

        # Handle M-Pesa STK push logic here (optional)
        # This is where you'd integrate with the M-Pesa API

        # Redirect to the payment page
        return redirect('payment')  # Replace with your payment processing URL name

    # If GET request, render the checkout page with the total amount and cart data
    return render(request, 'checkout.html', {
        'cart_total': cart_total,
        'cart_data': cart_data,  # Pass the cart data to the template for order summary
    })


def token(request):
    consumer_key = 'xM2Zn9dUq7QYKNtkrnjhCh0wAOgOZ9EOStVxEU1XZh4RIHPr'
    consumer_secret = 'fFGnV4AKYVAB89PdIhbNz6f6nEqmahmmz7PrknUuFu5l55KyoSz0b9EAV0Q9Zadu'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})


from django.shortcuts import redirect


def stk(request):
    if request.method == "POST":
        mpesa_number = request.POST.get('mpesa_number')
        total_amount = request.POST.get('total_amount')

        if not mpesa_number or not total_amount:
            return HttpResponse("Mpesa number and total amount are required.", status=400)

        # Access token and API setup
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request_data = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total_amount,
            "PartyA": mpesa_number,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": mpesa_number,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",  # Replace with your callback URL
            "AccountReference": "PRIDRIAN Luxe",
            "TransactionDesc": "Order Payment"
        }

        # Make the API request
        response = requests.post(api_url, json=request_data, headers=headers)

        if response.status_code == 200:
            # Payment initiated successfully
            return redirect('order_success')  # Replace 'order_success' with your actual success view name
        else:
            # Log the error response for debugging
            error_message = f"Payment failed: {response.text}"
            print(error_message)  # Log error (you can use logging instead of print)
            return HttpResponse("Payment failed. Please try again.", status=400)

    # Handle non-POST requests gracefully
    return HttpResponse("Invalid request method. Only POST is allowed.", status=405)


def order_success(request):
    # Fetch the most recent order or use a specific identifier (e.g., order ID)
    order_id = request.session.get('order_id')  # Store the order ID in session after payment
    if not order_id:
        return HttpResponse("No order information available.", status=400)

    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})
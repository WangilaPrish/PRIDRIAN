import requests
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from myapp.forms import ProductForm, ProfileForm, UserRegisterForm, ReviewForm
from myapp.models import User, Product, CartItem, Newsletter, Profile, Review, Order, OrderItem
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
        messages.info(request, "You are already logged in.")
        return redirect("index")  # Change this to your desired redirect URL

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=email, password=password)

            if user:
                login(request, user)
                messages.success(request, f"Hi {user.first_name or user.username}, login successful!")
                next_url = request.GET.get("next", "index")  # Adjust as needed
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
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
    profile, created = Profile.objects.get_or_create(user=request.user)  # Get or create the profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the profile instance directly
            messages.success(request, "Profile Updated Successfully.")
            return redirect("profile")  # Redirect to the profile page after saving
    else:
        form = ProfileForm(instance=profile)  # Prepopulate form with current profile data

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "profile.html", context)


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
                messages.success(request, "Your account was created successfully.")
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
    brand_name = request.GET.get('brand')
    sort_by = request.GET.get('sort_by', 'popularity')  # Default sort is by popularity

    # Filter by brand
    if brand_name:
        products = Product.objects.filter(brand__icontains=brand_name)
    else:
        products = Product.objects.all()

    # Sort products based on the selected criteria
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'arrival':
        products = products.order_by('-created_at')  # Assuming you have a created_at field
    else:
        products = products.annotate(review_count=Count('reviews')).order_by('-review_count')  # Default to sorting by popularity

    # Get distinct brands for the filter options
    brands = Product.objects.values_list('brand', flat=True).distinct()

    return render(request, 'shop.html', {'products': products, 'brands': brands})


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

def addproduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop')
    else:
        form = ProductForm()  # No changes needed here

    return render(request, 'addproduct.html', {'form': form})



@csrf_exempt  # Only for testing; avoid in production
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from the request body

            # Check if necessary data is present
            if 'id' not in data or 'name' not in data or 'quantity' not in data or 'price' not in data or 'image' not in data or 'color' not in data:
                return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

            # Create the cart product structure
            cart_product = {
                str(data['id']): {
                    'name': data['name'],
                    'quantity': int(data['quantity']),
                    'price': float(data['price']),
                    'image': data['image'],
                    'product_id': data['id'],
                    'color': data['color'],  # Add the color to the cart product structure
                }
            }

            # Initialize or update the session cart
            if 'cart_data_object' in request.session:
                cart_data = request.session['cart_data_object']

                if str(data['id']) in cart_data:
                    # Update the quantity of the existing product
                    cart_data[str(data['id'])]['quantity'] += int(data['quantity'])
                else:
                    # Add the new product to the cart
                    cart_data.update(cart_product)

                # Save the updated cart to the session
                request.session['cart_data_object'] = cart_data
            else:
                # Initialize the session cart with the new product
                request.session['cart_data_object'] = cart_product

            # Log the updated cart for debugging
            print(f"Updated cart: {request.session['cart_data_object']}")  # Debugging line

            # Return the updated cart data and total item count
            return JsonResponse({
                "data": request.session['cart_data_object'],
                'totalcartitems': len(request.session['cart_data_object'])
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
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Fetch orders for the logged-in user
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
        total_amount = cart_total + 150  # Add fixed shipping fee

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
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",  # Use your callback URL
            "AccountReference": "PRIDRIAN Luxe",
            "TransactionDesc": "Order Payment"
        }

        response = requests.post(api_url, json=request_data, headers=headers)

        if response.status_code == 200:
            # Payment initiated successfully
            return redirect('order_success')  # Redirect to your order success page
        else:
            # Handle errors in the payment process
            return HttpResponse("Payment failed. Please try again.", status=400)




def order_success(request):
    return render(request, 'order_success.html')
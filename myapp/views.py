from django.contrib.auth import logout, login
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from myapp.forms import ProductForm, ProfileForm, UserRegisterForm
from myapp.models import User, Product, CartItem, Newsletter, Profile, ProductReview, CartOrderProducts, CartOrder
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login

# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import User

def user_login(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey you are already Logged In.")
        return redirect("index")

    if request.method == "POST":
        email = request.POST.get("email")  # peanuts@gmail.com
        password = request.POST.get("password")  # getmepeanuts

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.")
                next_url = request.GET.get("next", 'index')
                return redirect(next_url)
            else:
                messages.warning(request, "User Does Not Exist, create an account.")

        except:
            messages.warning(request, f"User with {email} does not exist")

    return render(request, "login.html")


def about(request):
    return render(request, 'about.html')


#def cart(request):
    #cart_items = []
    #total_price = 0

    # Retrieve cart data from the session
    #cart = request.session.get('cart', [])  # Use 'cart' consistently
    #for item in cart:
       # product = Product.objects.get(id=item['product_id'])
       # cart_items.append({
          #  'id': product.id,
          #  'name': product.name,
          #  'price': product.price,
           ##'quantity': item['quantity'],
            #'color': item['color'],
            #'image': product.image.url,
           # 'total_price': product.price * item['quantity'],
       # })
        #total_price += product.price * item['quantity']

    #return render(request, 'cart.html', {
       # 'cart_items': cart_items,
        #'total_price': total_price,
   # })



def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect('cart')


def contact(request):
    return render(request, 'contact.html')


def shopsingle(request):
    return render(request, 'shop-single.html')


@login_required
def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("index")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "profile.html", context)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the new user from the form
            new_user = form.save()

            # Get the username from cleaned data for the success message
            username = form.cleaned_data.get("username")

            # Show success message
            messages.success(request, f"Hey {username}, your account was created successfully.")

            # Authenticate the user immediately after saving
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

            if user is not None:
                # Log the user in
                login(request, user)

                # Redirect to the next URL (or default to 'index')
                next_url = request.GET.get("next", 'index')
                return redirect(next_url)

            else:
                # If authentication fails, show an error (although this should not happen here)
                messages.error(request, "Authentication failed. Please try again.")
                return redirect('register')

    else:
        form = UserRegisterForm()

    # Render the registration form
    context = {'form': form}
    return render(request, "register.html", context)


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
        return render(request, 'index.html')


def logout_view(request):

    logout(request)
    messages.success(request, "You logged out.")
    return redirect("login")

def shopp(request):
    return render(request, 'shopp.html')
def shop(request):
    brand_name = request.GET.get('brand')
    if brand_name:
        products = Product.objects.filter(brand__icontains=brand_name)
    else:
        products = Product.objects.all()

    brands = Product.objects.values_list('brand', flat=True).distinct()
    return render(request, 'shop.html', {'products': products, 'brands': brands})

def cart(request):
    cart_total = 0
    print(f"Session data: {request.session.items()}")  # Log session data for debugging

    # Check if the cart exists in the session
    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']

        # Calculate the cart total
        for product_id, item in cart_data.items():
            cart_total += int(item['quantity']) * float(item['price'])

        return render(request, 'cart.html', {
            'cart_data': cart_data,
            'totalcartitems': len(cart_data),
            'cart_total': cart_total
        })

    # If the cart does not exist, render an empty cart
    else:
        return render(request, 'cart.html', {
            'cart_data': None,
            'totalcartitems': 0,
            'cart_total': cart_total
        })

def shopandcart(request, product_id):
    #Fetch the specific product by its ID
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shopandcart.html', {'product': product})

#def product_detail(request, product_id):
    #Fetch the specific product by its ID
    #product = get_object_or_404(Product, id=product_id)
    #return render(request, 'shopandcart.html', {'product': product})


def addproduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop')
    else:
        form = ProductForm()  # No changes needed here

    return render(request, 'addproduct.html', {'form': form})


#def add_to_cart(request):
   # if request.method == 'POST':
       # product_id = request.POST.get('product_id')
       # product = get_object_or_404(Product, id=product_id)
       # quantity = int(request.POST.get('quantity', 1))
#
      #  # Check if product already exists in the cart
        #cart_item, created = CartItem.objects.get_or_create(
            #product=product,
            #user=request.user if request.user.is_authenticated else None
      #  )

        #if not created:
       #     cart_item.quantity += quantity
       # cart_item.save()

        # Fetch the updated cart data
       # cart = get_cart_data(request)
       # return JsonResponse({'status': 'success', 'cart': cart})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only for testing; avoid in production
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from the request body

            # Check if necessary data is present
            if 'id' not in data or 'name' not in data or 'quantity' not in data or 'price' not in data or 'image' not in data:
                return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

            # Create the cart product structure
            cart_product = {
                str(data['id']): {
                    'name': data['name'],
                    'quantity': int(data['quantity']),
                    'price': float(data['price']),
                    'image': data['image'],
                    'product_id': data['id'],
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
def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id)

        # Remove item from the cart
        cart_item.delete()

        # Fetch the updated cart data
        cart = get_cart_data(request)
        return JsonResponse({'status': 'success', 'cart': cart})

def get_cart_data(request):
    # Function to fetch the current cart data (items and total)
    cart_items = CartItem.objects.filter(user=request.user if request.user.is_authenticated else None)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return {'items': [{'id': item.id, 'name': item.product.name, 'price': item.product.price, 'quantity': item.quantity, 'image': item.product.image.url} for item in cart_items], 'total': total}
def reviews(request):
    return render(request, 'reviews.html')

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
         'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )



def checkout(request):
    # Check if the cart exists in the session
    if 'cart_data_object' in request.session:
        cart_data = request.session['cart_data_object']

        # Calculate the cart total
        cart_total = sum(int(item['quantity']) * float(item['price']) for item in cart_data.values())

        if request.method == "POST":
            # Get phone number from the form
            phone_number = request.POST.get("phone_number")

            # Simulate M-Pesa payment (replace with actual integration later)
            # Here, add logic to process payment
            messages.success(request, f"Payment initiated for {phone_number} with amount ${cart_total}.")
            return redirect('order_success')  # Redirect to a success page

        return render(request, 'checkout.html', {
            'cart_data': cart_data,
            'cart_total': cart_total,
        })

    # If the cart does not exist, redirect to cart page
    else:
        messages.warning(request, "Your cart is empty. Please add items to proceed.")
        return redirect('cart')

def payment(request):
    return render(request, 'payment.html')


def paymentsuccess(request):
    return render(request, 'paymentsuccess.html')
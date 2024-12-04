from django.contrib.auth import logout
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from myapp.forms import ProductForm
from myapp.models import User, Product, CartItem, Newsletter
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

# Create your views here.
def login(request):
    if request.method == 'POST':
        if User.objects.filter(
            email=request.POST['email'],
            password=request.POST['password'],
        ).exists():
            return render(request, 'index.html')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

def about(request):
    return render(request, 'about.html')

def cart(request):
    return render(request, 'cart.html')

def contact(request):
    return render(request, 'contact.html')



def shopsingle(request):
    return render(request, 'shop-single.html')


def register(request):
    if request.method == 'POST':
        members=User(
            firstname = request.POST['firstname'],
            lastname = request.POST['lastname'],
            email = request.POST['email'],
            password=request.POST['password'],
        )

        members.save()
        return redirect('/login')

    else:
        return render(request, 'register.html')

def index(request):
    if request.method == 'POST':
        members=Newsletter(
            email = request.POST['email'],
        )

        members.save()
        return redirect('/index')

    else:
        return render(request, 'index.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def shopp(request):
    return render(request, 'shopp.html')
def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})



def shopandcart(request, product_id=None):
    if request.method == 'POST':
        action = request.POST.get('action', 'add')  # Default action is 'add'
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        if action == 'add':  # Add to cart
            quantity = int(request.POST.get('quantity', 1))
            selected_color = request.POST.get('color')  # Get the selected color

            # Check stock
            if product.stock < quantity:
                messages.error(request, f"Only {product.stock} items in stock.")
                return redirect('shopandcart')

            # Add item to cart
            cart_item, created = CartItem.objects.get_or_create(product=product, selected_color=selected_color)
            if created:
                cart_item.quantity = quantity
            else:
                if product.stock < cart_item.quantity + quantity:
                    messages.error(request, f"Not enough stock available.")
                    return redirect('shopandcart')
                cart_item.quantity += quantity

            cart_item.save()

            # Reduce stock
            product.stock = F('stock') - quantity
            product.save()

            messages.success(request, "Item added to cart.")
            return redirect('cart')

        elif action == 'remove':
            CartItem.objects.filter(product=product).delete()
            messages.success(request, "Item removed from cart.")
            return redirect('cart')

    # Fetch products and cart items
    products = Product.objects.all()
    cart_items = CartItem.objects.all()

    return render(request, 'shopandcart.html', {
        'products': products,
        'cart_items': cart_items,
    })

def product_detail(request, product_id):
    # Fetch the specific product by its ID
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shopandcart.html', {'product': product})

def addproduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop')
    else:
        form = ProductForm()  # No changes needed here

    return render(request, 'addproduct.html', {'form': form})
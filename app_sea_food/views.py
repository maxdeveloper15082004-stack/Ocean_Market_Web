from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
import random
import string
import re
from .models import Category, Product, CartItem, Wishlist, Order, OrderItem

def is_admin(user):
    return user.is_staff

def home(request):
    
    categories = Category.objects.filter(is_active=True)
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'categories': categories,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'home.html', context)

def category_products(request, category_slug):
    
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'category_products.html', context)

def product_detail(request, product_slug):
    from urllib.parse import unquote
    # Decode the URL-encoded slug (handles slashes in slug)
    product_slug = unquote(product_slug)
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    in_wishlist = False
    
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'product_detail.html', context)

def cart(request):
    
    cart_items = get_cart_items(request)
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    subtotal = sum(item.total_price for item in cart_items)
    shipping = 50 if subtotal > 0 and subtotal < 500 else 0
    total = subtotal + shipping
    
    context = {
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        weight = request.POST.get('weight', '1kg')
        
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                selected_weight=weight,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            session_key = request.session.session_key
            
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product=product,
                selected_weight=weight,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('cart')
    
    return redirect('home')

def remove_from_cart(request, cart_item_id):
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart')

def update_cart(request, cart_item_id):
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
    return redirect('cart')

def wishlist(request):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'wishlist_items': wishlist_items,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'wishlist.html', context)

def add_to_wishlist(request, product_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect('product_detail', product_slug=product.slug)

def remove_from_wishlist(request, wishlist_id):
    
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id)
    wishlist_item.delete()
    messages.success(request, 'Item removed from wishlist')
    return redirect('wishlist')

def orders(request):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.filter(user=request.user)
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'orders': orders,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'orders.html', context)

def order_detail(request, order_number):
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'order': order,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'order_detail.html', context)

def checkout(request):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart_items = get_cart_items(request)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('home')
    
    subtotal = sum(item.total_price for item in cart_items)
    shipping = 50 if subtotal > 0 and subtotal < 500 else 0
    total = subtotal + shipping
    
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'checkout.html', context)

def place_order(request):
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        cart_items = get_cart_items(request)
        
        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('home')
        
        order_number = 'OM' + ''.join(random.choices(string.digits, k=8))
        
        subtotal = sum(item.total_price for item in cart_items)
        shipping = 50 if subtotal > 0 and subtotal < 500 else 0
        total = subtotal + shipping
        
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=total,
            shipping_address=request.POST.get('shipping_address', ''),
            phone=request.POST.get('phone', ''),
            notes=request.POST.get('notes', '')
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                weight=item.selected_weight
            )
        
        cart_items.delete()
        
        messages.success(request, f'Order placed successfully! Order number: {order_number}')
        return redirect('order_detail', order_number=order_number)
    
    return redirect('checkout')

def login_view(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'login.html', context)

def register_view(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        login(request, user)
        messages.success(request, 'Registration successful! Welcome to Ocean Market!')
        return redirect('home')
    
    cart_items_count = get_cart_items_count(request)
    wishlist_count = get_wishlist_count(request)
    
    context = {
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'register.html', context)

def logout_view(request):
    
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

@user_passes_test(is_admin)
def admin_dashboard(request):
    
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_revenue = sum(order.total_amount for order in Order.objects.all())
    
    recent_orders = Order.objects.all()[:10]
    products = Product.objects.all()[:20]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'products': products,
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_admin)
def add_product(request):
    
    if request.method == 'POST':
        category = get_object_or_404(Category, id=request.POST.get('category'))
        
        product_name = request.POST.get('name')
        slug = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
        
        product = Product.objects.create(
            category=category,
            name=product_name,
            slug=slug,
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            weight=request.POST.get('weight'),
            stock_status=request.POST.get('stock_status'),
            stock_quantity=request.POST.get('stock_quantity', 0),
        )
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
            product.save()
        
        messages.success(request, 'Product added successfully!')
        return redirect('admin_dashboard')
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'add_product.html', context)

@user_passes_test(is_admin)
def edit_product(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product.name = product_name
        product.slug = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.weight = request.POST.get('weight')
        product.stock_status = request.POST.get('stock_status')
        product.stock_quantity = request.POST.get('stock_quantity', 0)
        
        category = get_object_or_404(Category, id=request.POST.get('category'))
        product.category = category
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_dashboard')
    
    categories = Category.objects.all()
    context = {'product': product, 'categories': categories}
    return render(request, 'edit_product.html', context)

@user_passes_test(is_admin)
def delete_product(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def admin_orders(request):
    
    orders = Order.objects.all()
    context = {'orders': orders}
    return render(request, 'admin_orders.html', context)

@user_passes_test(is_admin)
def update_order_status(request, order_number):
    
    if request.method == 'POST':
        order = get_object_or_404(Order, order_number=order_number)
        order.status = request.POST.get('status')
        order.save()
        messages.success(request, f'Order status updated to {order.status}!')
    
    return redirect('admin_orders')

def get_cart_items(request):
    
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            return CartItem.objects.filter(session_key=session_key)
        return []

def get_cart_items_count(request):
    
    cart_items = get_cart_items(request)
    return sum(item.quantity for item in cart_items)

def get_wishlist_count(request):
    
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).count()
    return 0
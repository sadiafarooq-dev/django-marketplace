from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from store.models import CustomUser, Product, Order, OrderItem
from django.contrib.auth.decorators import user_passes_test

# Admin Login View

@login_required(login_url='admin_login')
def admin_profile(request):
    if request.user.role != 'admin':
        return redirect('admin_login')

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        if not username:
            messages.error(request, "Username cannot be empty.")
            return redirect('admin_profile')
        if CustomUser.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "That username is already taken.")
            return redirect('admin_profile')
        request.user.username = username
        request.user.email = email
        request.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('admin_profile')

    return render(request, "adminpanel/profile.html")



def admin_login(request):
    if request.user.is_authenticated and request.user.role == "admin":
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and user.role == "admin":
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or unauthorized access.")
            return redirect('admin_login')

    return render(request, "adminpanel/login.html")


# Admin Dashboard View (Stats + Seller Insights)
@login_required(login_url='admin_login')
def admin_dashboard(request):
    if request.user.role != "admin":
        messages.warning(request, "You are not authorized to access this page.")
        return redirect('admin_login')

    sellers = CustomUser.objects.filter(role="seller")
    buyers = CustomUser.objects.filter(role="buyer")
    products = Product.objects.all()
    orders = Order.objects.all()

    # Seller-wise Product & Order Count
    seller_stats = []
    for seller in sellers:
        product_count = Product.objects.filter(seller=seller).count()
        order_count = OrderItem.objects.filter(product__seller=seller).values('order').distinct().count()
        seller_stats.append({
            "seller": seller,
            "product_count": product_count,
            "order_count": order_count
        })


    context = {
        "total_sellers": sellers.count(),
        "total_buyers": buyers.count(),
        "total_products": products.count(),
        "total_orders": orders.count(),
        "seller_stats": seller_stats,
    }

    return render(request, "adminpanel/dashboard.html", context)


# Admin Logout View
@login_required(login_url='admin_login')
def admin_logout(request):
    if request.user.role == "admin":
        logout(request)
        messages.success(request, "Logged out successfully.")
    return redirect("admin_login")


# Manage Seller
@login_required(login_url='admin_login')
def manage_sellers(request):
    if request.user.role != 'admin':
        return redirect('admin_login')

    pending_sellers = CustomUser.objects.filter(role='seller', is_seller_approved=False)
    approved_sellers = CustomUser.objects.filter(role='seller', is_seller_approved=True)

    context = {
        "pending_sellers": pending_sellers,
        "approved_sellers": approved_sellers
    }
    return render(request, "adminpanel/manage_sellers.html", context)

# Approve Seller

@login_required(login_url='admin_login')
def approve_seller(request, seller_id):
    if request.user.role != "admin":
        return redirect("admin_login")

    seller = get_object_or_404(CustomUser, id=seller_id, role="seller")
    seller.is_seller_approved = True
    seller.save()
    messages.success(request, f"{seller.username} approved successfully.")
    return redirect('manage_sellers')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def seller_detail_view(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id, role='seller')
    products = Product.objects.filter(seller=seller)
    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product')
    customers = CustomUser.objects.filter(order__orderitem__product__seller=seller, role='buyer').distinct()

    context = {
        'seller': seller,
        'products': products,
        'order_items': order_items,
        'customers': customers,
    }
    return render(request, 'adminpanel/seller_detail.html', context)
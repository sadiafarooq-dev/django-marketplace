from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Category, OrderItem, Order, CustomUser
from .forms import ProductForm
from django.views.decorators.http import require_POST


#  Buyer Homepage (Shows Trending Products)
def home(request):
    trending_products = Product.objects.filter(trending=True, status=True)  # Public trending products
    return render(request, "store/index.html", {'trending_products': trending_products})

#  Buyer Collections View
def collections(request):
    category = Category.objects.filter(status=0)  # Show active categories
    return render(request, "store/collections.html", {'category': category})

#  Buyer Collection Products View (Only Public Products)
def collectionsview(request, slug):
    category = get_object_or_404(Category, slug=slug, status=0)
    products = Product.objects.filter(category=category, status=True)
    return render(request, 'store/products/index.html', {'products': products, 'category': category})

# Buyer Product Detail View
def productview(request, cate_slug, prod_slug):
    category = get_object_or_404(Category, slug=cate_slug)
    product = get_object_or_404(Product, category=category, slug=prod_slug, status=True)

    return render(request, 'store/products/view.html', {
        'product': product,
        'category': category
    })

def product_autocomplete(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(name__icontains=request.GET.get('term'))
        results = []
        for product in qs:
            results.append({
                'label': product.name,
                'value': product.name,
                'url': product.get_absolute_url()  # assumes you’ve defined this method
            })
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

def productlistAjax(request):
    # Get all product names for the autocomplete dropdown
    products = Product.objects.filter(status=True).values_list('name', flat=True)
    product_names = list(products)
    return JsonResponse(product_names, safe=False)


#  Product Search for Buyers
def search_product(request):
    query = (request.GET.get('term') or '').strip()
    if not query:
        return redirect("/")
    try:
        product = Product.objects.get(name__iexact=query)
        return redirect(product.get_absolute_url())
    except (Product.DoesNotExist, Product.MultipleObjectsReturned):
        return redirect("/")  # or render a 'no result found' page

#  Seller Home
@login_required(login_url='loginpage')
def seller_home(request):
    if request.user.role != 'seller':
        return redirect('home')

    is_verified = request.user.is_seller_approved
    return render(request, 'store/seller_home.html', { 'is_verified': is_verified })



# Seller Dashboard - Manages Their Own Products
@login_required(login_url='loginpage')
def seller_dashboard(request):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        messages.warning(request, "Access denied: Your seller account is not yet approved.")
        return redirect('/')
    
    products = Product.objects.filter(seller=request.user)
    return render(request, 'store/seller_dashboard.html', {'products': products})



#  Seller Adds a New Product
@login_required(login_url='loginpage')
def add_product(request):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        messages.warning(request, "You must be an approved seller to add products.")
        return redirect('/')

    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.status = True  # 🔴 Force product to be visible
            product.save()
            return redirect('seller_dashboard')
    return render(request, 'store/add_product.html', {'form': form})

# Edit Product
@login_required(login_url='loginpage')
def edit_product(request, product_id):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        messages.warning(request, "You are not authorized to edit products.")
        return redirect('/')

    product = get_object_or_404(Product, id=product_id, seller=request.user)

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == "POST":
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_dashboard')
        else:
            print(form.errors)

    return render(request, "store/edit_product.html", {'form': form, 'product': product})



#  Seller Deletes Their Own Product
@login_required(login_url='loginpage')
def delete_product(request, product_id):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        messages.warning(request, "You are not authorized to delete products.")
        return redirect('/')

    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    return redirect('seller_dashboard')



# Seller orders
@login_required(login_url='loginpage')
def seller_orders(request):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        messages.warning(request, "You are not authorized to view orders.")
        return redirect('/')

    orders = OrderItem.objects.filter(product__seller=request.user).select_related('order', 'product')

    statuses = ['Pending', 'Out for delivery', 'Delivered']  # ✅ Add this

    return render(request, 'store/seller_orders.html', {
        'orders': orders,
        'statuses': statuses,  # ✅ Pass it to template
    })



# Order Status

@login_required(login_url='loginpage')
@require_POST
def update_order_status(request, order_id):
    if request.user.role != 'seller' or not request.user.is_seller_approved:
        return redirect('/')

    order = get_object_or_404(Order, id=order_id)
    
    # A seller may only change the status of an order whose items are ALL theirs
    items = OrderItem.objects.filter(order=order)
    if not items.exists() or items.exclude(product__seller=request.user).exists():
        messages.error(request, "You are not authorized to update this order.")
        return redirect('seller_orders')

    status = request.POST.get('status')
    if status in ['Pending', 'Out for delivery', 'Delivered']:
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.tracking_no} updated to '{status}'.")

    return redirect('seller_orders')

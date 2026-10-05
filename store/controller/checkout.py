from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Cart, Order, OrderItem, Product, Profile
import random
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db import transaction


def _verify_razorpay_payment(payment_id, expected_amount):
    """Ask Razorpay whether this payment really exists and is for the right amount.
    Never trust a 'paid' flag sent from the browser."""
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not (payment_id and key_id and key_secret):
        return False
    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        payment = client.payment.fetch(payment_id)
    except Exception:
        return False
    return (payment.get('status') in ('authorized', 'captured')
            and int(payment.get('amount', 0)) == int(round(expected_amount * 100)))

User = get_user_model()  # Use your CustomUser

@login_required(login_url='loginpage')
def index(request):
    rawcart = Cart.objects.filter(user=request.user)
    for item in rawcart:
        if item.product_qty > item.product.quantity:
            item.delete()

    cartitems = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.selling_price * item.product_qty for item in cartitems)

    userprofile = Profile.objects.filter(user=request.user).first()

    context = {
        'cartitems': cartitems,
        'total_price': total_price,
        'userprofile': userprofile
    }
    return render(request, "store/checkout.html", context)


@login_required(login_url='loginpage')
def placeorder(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart = Cart.objects.filter(user=request.user).select_related('product')
    if not cart.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Re-check stock at the moment of ordering
    for item in cart:
        if item.product_qty > item.product.quantity:
            messages.error(request, f"Only {item.product.quantity} of {item.product.name} left in stock.")
            return redirect('cart')

    cart_total_price = sum(item.product.selling_price * item.product_qty for item in cart)
    payMode = request.POST.get('payment_mode')
    payment_id = request.POST.get('payment_id')

    if payMode == "Paid by Razorpay" and not _verify_razorpay_payment(payment_id, cart_total_price):
        return JsonResponse({'status': "Payment could not be verified."}, status=400)
    if payMode != "Paid by Razorpay":
        payMode = "COD"
        payment_id = None

    currentuser = User.objects.filter(id=request.user.id).first()
    if not currentuser.first_name:
        currentuser.first_name = request.POST.get('fname')
        currentuser.last_name = request.POST.get('lname')
        currentuser.save()

    if not Profile.objects.filter(user=request.user).exists():
        Profile.objects.create(
            user=request.user,
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            country=request.POST.get('country'),
            pincode=request.POST.get('pincode'),
        )

    with transaction.atomic():
        neworder = Order()
        neworder.user = request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.email = request.POST.get('email')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.country = request.POST.get('country')
        neworder.pincode = request.POST.get('pincode')
        neworder.payment_mode = payMode
        neworder.payment_id = payment_id
        neworder.total_price = cart_total_price

        trackno = 'sadia' + str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = 'sadia' + str(random.randint(1111111, 9999999))
        neworder.tracking_no = trackno
        neworder.save()

        for item in cart:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )
            product = Product.objects.select_for_update().get(id=item.product_id)
            product.quantity -= item.product_qty
            product.save()

        Cart.objects.filter(user=request.user).delete()

    if payMode == "Paid by Razorpay":
        return JsonResponse({'status': "Your order has been placed successfully"})
    messages.success(request, 'Your order has been placed successfully')
    return redirect('/')


@login_required(login_url='loginpage')
def razorpaycheck(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.selling_price * item.product_qty for item in cart)
    return JsonResponse({
        'total_price': total_price,
        'key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
    })


@login_required(login_url='loginpage')
def orders(request):
    return redirect('myorders')

from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from store.models import Cart, Product
from django.contrib.auth.decorators import login_required

def addtocart(request):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                prod_id_raw = request.POST.get('product_id')
                prod_qty_raw = request.POST.get('product_qty')

                if prod_id_raw is None or prod_qty_raw is None:
                    return JsonResponse({'status': "Product ID or quantity missing"})

                prod_id = int(prod_id_raw)
                prod_qty = int(prod_qty_raw)

                product_check = Product.objects.filter(id=prod_id).first()

                if product_check:
                    if Cart.objects.filter(user=request.user, product_id=prod_id).exists():
                        return JsonResponse({'status': "Product already in cart"})
                    else:
                        if product_check.quantity >= prod_qty:
                            Cart.objects.create(
                                user=request.user,
                                product_id=prod_id,
                                product_qty=prod_qty
                            )
                            return JsonResponse({'status': "Product added successfully!"})
                        else:
                            return JsonResponse({'status': "Only " + str(product_check.quantity) + " quantity available"})
                else:
                    return JsonResponse({'status': "Product not found"})
            else:
                return JsonResponse({'status': "Login to Continue"})
        except Exception as e:
            return JsonResponse({'status': "Error: " + str(e)})
    return redirect('/')


@login_required(login_url='loginpage')
def viewcart(request):
    cart = Cart.objects.filter(user=request.user)
    context  = {'cart':cart}
    return render(request, 'store/cart.html', context)


@login_required(login_url='loginpage')
def updatecart(request):
    if request.method == 'POST':
        prod_id = int(request.POST.get('product_id'))
        prod_qty = int(request.POST.get('product_qty'))
        
        # Get the product to check stock
        product = Product.objects.filter(id=prod_id).first()
        if product is None:
            return JsonResponse({'status': "Product not found", 'error': True})
        
        if Cart.objects.filter(user=request.user, product_id=prod_id).exists():
            cart = Cart.objects.get(product_id=prod_id, user=request.user)
            
            # Validate stock before updating
            if prod_qty < 1 or prod_qty > product.quantity:
                return JsonResponse({'status': "Out of Stock", 'error': True})
            
            cart.product_qty = prod_qty
            cart.save()
            return JsonResponse({'status': "Quantity updated successfully!"})
    return JsonResponse({'status': "Something went wrong", 'error': True})

@login_required(login_url='loginpage')
def deletecartitem(request):
    if request.method =='POST':
        prod_id = int(request.POST.get('product_id'))
        if (Cart.objects.filter(user=request.user, product_id=prod_id)):
             cartitem = Cart.objects.get(product_id=prod_id, user=request.user)
             cartitem.delete()
        return JsonResponse({'status': "Item deleted successfully!"})
    return redirect('/')
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from store.models import Product, Wishlist

@login_required(login_url='loginpage')
def index(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context = {'wishlist': wishlist}
    return render(request, 'store/wishlist.html', context)

@login_required(login_url='loginpage')
def addtowishlist(request):
    if request.method == 'POST':
        prod_id = int(request.POST.get('product_id'))
        if Product.objects.filter(id=prod_id).exists():
            if Wishlist.objects.filter(user=request.user, product_id=prod_id).exists():
                return JsonResponse({'status': "Product already in the wishlist."})
            else:
                Wishlist.objects.create(user=request.user, product_id=prod_id)
                return JsonResponse({'status': "Product added to wishlist."})
        else:
            return JsonResponse({'status': "No such product found."})
    return JsonResponse({'status': "Invalid request method."}, status=400)

@login_required(login_url='loginpage')
def deletewishlistitem(request):
    if request.method == 'POST':
        prod_id = int(request.POST.get('product_id'))

        if Wishlist.objects.filter(user=request.user, product_id=prod_id).exists():
            wishlistitem = Wishlist.objects.get(user=request.user, product_id=prod_id)
            wishlistitem.delete()
            return JsonResponse({'status': "Product removed from wishlist."})
        else:
            return JsonResponse({'status': "Product doesn't exist in wishlist."})
    return JsonResponse({'status': "Invalid request."}, status=400)

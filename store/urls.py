from django.urls import path
from .import views
from store.views import collectionsview
from store.controller import authview, cart, wishlist, checkout, order

urlpatterns = [
    # Buyer Routes
    path('', views.home, name="home"),

    path('collections', views.collections, name="collections"), 
    path('collections/<str:slug>/', collectionsview, name="collectionsview"),

    # 
    path('collections/<str:cate_slug>/<str:prod_slug>/', views.productview, name="productview"),

    path('product-list', views.productlistAjax),
    path("product-autocomplete/", views.product_autocomplete, name="product_autocomplete"),
    path("searchproduct", views.search_product, name="searchproduct"),


    # Authentication (Buyer & Seller)
    path('register/', authview.register, name="register"),
    path('login/', authview.loginpage, name="loginpage"),
    path('logout/', authview.logoutpage, name="logoutpage"),

    # Buyer Features (Cart, Wishlist, Orders)
    path('add-to-cart', cart.addtocart, name="addtocart"),
    path('cart/', cart.viewcart, name="cart"),
    path('update-cart', cart.updatecart, name="update-cart"),
    path('delete-cart-item', cart.deletecartitem, name="deletecartitem"),
    
    path('wishlist', wishlist.index, name="wishlist"),
    path('add-to-wishlist', wishlist.addtowishlist, name="addtowishlist"),
    path('delete-wishlist-item', wishlist.deletewishlistitem, name="deletewishlistitem"),

    path('checkout', checkout.index, name="checkout"),
    path('place-order', checkout.placeorder, name="placeorder"),
    path('proceed-to-pay', checkout.razorpaycheck),

    path('my-orders', order.index, name="myorders"),
    path('invoice/<str:t_no>/', order.download_invoice, name="download_invoice"),
    path('view-order/<str:t_no>', order.vieworder, name="orderview"),

    # Seller Routes (Dashboard & Product Management)
    path('seller-home/', views.seller_home, name='seller_home'),
    path('seller-dashboard/', views.seller_dashboard, name="seller_dashboard"),
    path('add-product/', views.add_product, name="add_product"),
    path('edit-product/<int:product_id>/', views.edit_product, name="edit_product"),
    path('delete-product/<int:product_id>/', views.delete_product, name="delete_product"),
    path('seller-orders/', views.seller_orders, name='seller_orders'),
    path('seller-orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),

] #almost 30

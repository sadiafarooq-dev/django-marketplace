from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name="admin_login"),
    path('dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('sellers/', views.manage_sellers, name='manage_sellers'),
    path('sellers/approve/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('admin/seller/<int:seller_id>/', views.seller_detail_view, name='seller_detail'),

]

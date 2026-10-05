from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
import os
from django.urls import reverse
from django.utils.text import slugify


# Custom User Model with Buyer/Seller Role
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    is_seller_approved = models.BooleanField(default=False) 
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser


# Function for Dynamic File Path
def get_file_path(request, filename):
    original_filename = filename
    nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{nowTime}_{original_filename}"
    return os.path.join('uploads/', filename)

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)  #  SlugField with auto generation
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    description = models.TextField(max_length=500)
    status = models.BooleanField(default=False)  # NOTE: for categories, False (0) = visible, True = hidden
    trending = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=150)
    meta_keywords = models.CharField(max_length=150)
    meta_description = models.TextField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
# Product Model (Only Sellers Can Add)
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    product_image = models.ImageField(upload_to="products/", null=True, blank=True)
    small_description = models.CharField(max_length=250)
    quantity = models.IntegerField()
    description = models.TextField(max_length=500)
    original_price = models.FloatField()
    selling_price = models.FloatField()
    status = models.BooleanField(default=False, help_text="Checked = visible in the shop")
    trending = models.BooleanField(default=False, help_text="Checked = shown in Trending")
    tag = models.CharField(max_length=150)
    meta_title = models.CharField(max_length=150, default="Default Title")
    meta_keywords = models.CharField(max_length=150, default="default,keywords")
    meta_description = models.TextField(max_length=150, default="Default description")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        seller_name = self.seller.username if self.seller else "No Seller Assigned"
        return f"{self.name} - Seller: {seller_name}"

    def get_absolute_url(self):
        return reverse("productview", args=[self.category.slug, self.slug])



# Cart Model (Only Buyers Can Add Products)
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'buyer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_qty = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

# Wishlist Model (Only Buyers Can Save Products)
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'buyer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Order Model (Buyers Placing Orders)
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'buyer'})
    fname = models.CharField(max_length=150)
    lname = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    phone = models.CharField(max_length=150)
    address = models.TextField(max_length=500)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.CharField(max_length=150)
    total_price = models.FloatField()
    payment_mode = models.CharField(max_length=150)
    payment_id = models.CharField(max_length=250, null=True)
    orderstatuses = [
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=150, choices=orderstatuses, default='Pending')
    tracking_no = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.tracking_no}"

# OrderItem Model (Products in an Order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.order.id} - {self.order.tracking_no}"

# Profile Model (Buyer & Seller Details)
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    address = models.TextField(max_length=500)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.CharField(max_length=150)
    business_name = models.CharField(max_length=150, null=True, blank=True)  # Seller-specific field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.role}"

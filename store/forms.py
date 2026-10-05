from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, Product  # Import CustomUser & Product model

# Custom User Registration Form (Buyer/Seller Role Selection)
class CustomUserForm(UserCreationForm):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control my-2'}),
    )
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control my-2', 'placeholder': 'Enter Username'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control my-2', 'placeholder': 'Enter Email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control my-2', 'placeholder': 'Enter Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control my-2', 'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = CustomUser  # Using CustomUser model with roles
        fields = ['username', 'email', 'password1', 'password2', 'role']

# Product Management Form for Sellers
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'slug', 'name', 'product_image',
            'small_description', 'quantity', 'description', 'original_price',
            'selling_price', 'status', 'trending', 'tag', 
            'meta_title', 'meta_keywords', 'meta_description'
        ]
        widgets = {
            'tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product tags'}),
            'trending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control'}),
        }
"""Fill an empty database with demo accounts, categories and products.

Usage:  python manage.py seed_demo
Safe to run more than once - it skips anything that already exists.
"""
from django.core.management.base import BaseCommand

from store.models import Category, CustomUser, Product

PASSWORD = "Demo@12345"

CATEGORIES = [
    # name, image in media/uploads, product images in media/products
    ("Furniture", "uploads/20250625164747_20250621014923_Furniture.webp",
     ["fu6.jpg", "fu7.jpg", "furn3.jpg", "furn4.jpg", "furn7.webp", "fur8.webp", "f1.jpg"]),
    ("Electronics", "uploads/20250625164935_20250621012945_electro.webp",
     ["el6.jpg", "el7.jpg", "elect4.webp", "elect5.webp", "photo-1505740420928-5e560c06d30e.jpg"]),
    ("Books & Novels", "uploads/20250625164731_20250621014915_Books__Novels.webp",
     ["book.jpg", "book5.jpg", "book6.jpg", "bk2.jpg", "b1.jpg"]),
    ("Jewelry & Watches", "uploads/20250625164714_20250621014907_Jewelry__Watches.webp",
     ["j1.webp", "j2.webp", "j3.webp", "j4.webp", "j5.webp", "j6.webp", "jw8.jpg", "jw9.jpg"]),
    ("Kitchen", "uploads/20250625165118_20250621012423_kitchen.webp",
     ["kt1.jpg", "kt2.webp", "kt8.webp", "k1.jpg", "k2.jpg"]),
    ("Home Decor", "uploads/20250625165106_20250621012715_decorhome.webp",
     ["h1.webp", "h2.webp", "h3.webp", "h4.webp", "h7.webp"]),
    ("Health & Beauty", "uploads/20250625164807_20250621013422_health_and_beauty.jpg",
     ["hbeauty1.jpeg", "hbeauty2.jpg", "h5.webp", "h6.webp"]),
    ("Sports", "uploads/20250625164758_20250621013630_sport.webp",
     ["sport4.webp", "sport5.jpg", "sp5.webp", "sp6.jpg", "s2.jpg"]),
]


class Command(BaseCommand):
    help = "Create demo users, categories and products"

    def make_user(self, username, role, **extra):
        user, created = CustomUser.objects.get_or_create(
            username=username, defaults={"role": role, "email": f"{username}@example.com", **extra})
        if created:
            user.set_password(PASSWORD)
            user.save()
        return user

    def handle(self, *args, **options):
        self.make_user("admin", "admin")
        seller = self.make_user("demo_seller", "seller", is_seller_approved=True)
        self.make_user("demo_buyer", "buyer")

        prices = [1499, 2499, 899, 3999, 5999, 1299, 749, 4599]
        made = 0
        for c_i, (name, cat_img, product_imgs) in enumerate(CATEGORIES):
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    "image": cat_img,
                    "description": f"Shop the best {name.lower()} from trusted sellers.",
                    "status": False,          # False = visible for categories
                    "trending": c_i < 4,
                    "meta_title": name,
                    "meta_keywords": name.lower(),
                    "meta_description": f"{name} collection",
                },
            )
            for p_i, img in enumerate(product_imgs, start=1):
                p_name = f"{name.split(' ')[0]} Item {p_i}"
                if Product.objects.filter(name=p_name, category=category).exists():
                    continue
                price = prices[(c_i + p_i) % len(prices)]
                Product.objects.create(
                    category=category,
                    seller=seller,
                    name=p_name,
                    product_image=f"products/{img}",
                    small_description=f"Quality {name.lower()} at a great price.",
                    quantity=25,
                    description=f"A popular pick in our {name} collection.",
                    original_price=round(price * 1.25),
                    selling_price=price,
                    status=True,
                    trending=p_i <= 2,
                    tag="New" if p_i == 1 else "Sale",
                )
                made += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Added {made} products.\n"
            f"Log in with any of these (password {PASSWORD}):\n"
            f"  admin       -> http://127.0.0.1:8000/adminpanel/login/\n"
            f"  demo_seller -> http://127.0.0.1:8000/login/\n"
            f"  demo_buyer  -> http://127.0.0.1:8000/login/"))

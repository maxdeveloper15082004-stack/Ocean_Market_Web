import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_sea_food.settings')
django.setup()

from app_sea_food.models import Category, Product

categories = [
    {'name': 'Fresh Fish', 'slug': 'fresh-fish', 'description': 'Best quality fresh fish from the ocean'},
    {'name': 'Prawn', 'slug': 'prawn', 'description': 'Fresh and juicy prawns'},
    {'name': 'Crab', 'slug': 'crab', 'description': 'Delicious fresh crabs'},
    {'name': 'Squid', 'slug': 'squid', 'description': 'Fresh squids for your recipes'},
]

for cat in categories:
    Category.objects.get_or_create(slug=cat['slug'], defaults=cat)

print('Categories created!')

fish = Category.objects.get(slug='fresh-fish')
prawn = Category.objects.get(slug='prawn')
crab = Category.objects.get(slug='crab')
squid = Category.objects.get(slug='squid')

products = [
    {'category': fish, 'name': 'Salmon Fish', 'price': 25.99, 'weight': '1kg', 'stock_status': 'in_stock', 'stock_quantity': 50},
    {'category': fish, 'name': 'Tuna Fish', 'price': 22.99, 'weight': '1kg', 'stock_status': 'in_stock', 'stock_quantity': 30},
    {'category': fish, 'name': 'Snapper', 'price': 18.99, 'weight': '500g', 'stock_status': 'in_stock', 'stock_quantity': 25},
    {'category': prawn, 'name': 'Tiger Prawn', 'price': 28.99, 'weight': '1kg', 'stock_status': 'in_stock', 'stock_quantity': 40},
    {'category': prawn, 'name': 'King Prawn', 'price': 32.99, 'weight': '1kg', 'stock_status': 'low_stock', 'stock_quantity': 10},
    {'category': crab, 'name': 'Blue Crab', 'price': 15.99, 'weight': '1kg', 'stock_status': 'in_stock', 'stock_quantity': 20},
    {'category': crab, 'name': 'Mud Crab', 'price': 19.99, 'weight': '1kg', 'stock_status': 'in_stock', 'stock_quantity': 15},
    {'category': squid, 'name': 'Whole Squid', 'price': 12.99, 'weight': '500g', 'stock_status': 'in_stock', 'stock_quantity': 35},
]

for p in products:
    slug = p['name'].lower().replace(' ', '-')
    Product.objects.get_or_create(slug=slug, defaults={
        **p,
        'description': f'Fresh and delicious {p["name"]} delivered to your door'
    })

print('Products created!')

from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@oceanmarket.com', 'admin123')
    print('Admin user created!')
else:
    print('Admin user already exists!')
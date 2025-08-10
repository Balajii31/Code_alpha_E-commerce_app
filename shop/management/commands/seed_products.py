from django.core.management.base import BaseCommand
from shop.models import Product

SAMPLE_PRODUCTS = [
    {
        "name": "T-shirt",
        "description": "Comfortable cotton t-shirt",
        "price": 499.00,
        "image_url": "https://picsum.photos/seed/t/600/400",
        "stock": 50,
    },
    {
        "name": "Sneakers",
        "description": "Stylish everyday sneakers",
        "price": 2999.00,
        "image_url": "https://picsum.photos/seed/s/600/400",
        "stock": 25,
    },
    {
        "name": "Backpack",
        "description": "Durable backpack with multiple compartments",
        "price": 1999.00,
        "image_url": "https://picsum.photos/seed/b/600/400",
        "stock": 30,
    },
]


class Command(BaseCommand):
    help = "Seed sample products into the database"

    def handle(self, *args, **options):
        created = 0
        for data in SAMPLE_PRODUCTS:
            obj, was_created = Product.objects.get_or_create(name=data["name"], defaults=data)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded products. Created: {created}"))


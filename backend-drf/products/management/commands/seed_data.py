from decimal import Decimal, ROUND_HALF_UP
import random

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from products.models import Product


SEED_PASSWORD = "DemoPass123!"  # For local development only. Change before any real use.
CENT = Decimal("0.01")


PRODUCT_DATA = [
    ("Wireless Mouse", "Ergonomic wireless mouse", "599.00", 18, 45),
    ("Mechanical Keyboard", "Mechanical keyboard for everyday work", "2199.00", 18, 22),
    ("USB-C Hub", "Multi-port USB-C adapter", "1299.00", 18, 30),
    ("Laptop Stand", "Adjustable metal laptop stand", "899.00", 18, 18),
    ("Desk Lamp", "LED desk lamp with adjustable arm", "749.00", 12, 27),
    ("Water Bottle", "Reusable stainless-steel water bottle", "299.00", 5, 60),
    ("Notebook Set", "Set of three ruled notebooks", "199.00", 5, 100),
    ("Bluetooth Speaker", "Portable Bluetooth speaker", "1599.00", 18, 16),
    ("Phone Charger", "USB fast wall charger", "499.00", 18, 40),
    ("Cotton T-Shirt", "Everyday cotton crew-neck T-shirt", "599.00", 5, 35),
    ("Backpack", "Daily-use backpack with laptop sleeve", "1299.00", 18, 20),
    ("Running Shoes", "Lightweight running shoes", "2499.00", 12, 14),
    ("Coffee Mug", "Ceramic coffee mug", "249.00", 5, 50),
    ("Yoga Mat", "Non-slip exercise mat", "799.00", 18, 25),
    ("Office Chair", "Ergonomic office chair", "4999.00", 18, 8),
]

FIRST_NAMES = ["Aarav", "Diya", "Kabir", "Anaya", "Ishaan", "Meera", "Rohan", "Sana"]
LAST_NAMES = ["Sharma", "Verma", "Khan", "Kapoor", "Patel", "Singh", "Mehta", "Rao"]


def find_model(class_name):
    """Find a model by class name so this command does not assume app labels."""
    matches = [model for model in apps.get_models() if model.__name__ == class_name]
    if len(matches) != 1:
        labels = [model._meta.label for model in matches]
        if not matches:
            raise CommandError(
                f"Could not find model {class_name}. Make sure its Django app is in INSTALLED_APPS."
            )
        raise CommandError(
            f"Found multiple models named {class_name}: {labels}. "
            "Use explicit model imports to choose the correct one."
        )
    return matches[0]


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_totals(lines):
    subtotal = Decimal("0.00")
    tax_amount = Decimal("0.00")

    for product, quantity in lines:
        line_subtotal = product.price * quantity
        subtotal += line_subtotal
        tax_amount += line_subtotal * product.tax_percent / Decimal("100")

    subtotal = money(subtotal)
    tax_amount = money(tax_amount)
    return subtotal, tax_amount, money(subtotal + tax_amount)


class Command(BaseCommand):
    help = "Create repeatable demo users, products, carts, and orders."

    @transaction.atomic
    def handle(self, *args, **options):
        Cart = find_model("Cart")
        CartItem = find_model("CartItem")
        Order = find_model("Order")
        OrderItem = find_model("OrderItem")
        User = get_user_model()
        rng = random.Random(42)  # Keeps generated quantities and selections repeatable.

        users = []
        for number, (first_name, last_name) in enumerate(zip(FIRST_NAMES, LAST_NAMES), start=1):
            email = f"customer{number:02d}@example.com"
            username = f"customer{number:02d}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                user.set_password(SEED_PASSWORD)
                user.save(update_fields=["password"])
            users.append(user)

        products = []
        for name, description, price, tax_percent, stock in PRODUCT_DATA:
            product, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": Decimal(price),
                    "tax_percent": Decimal(str(tax_percent)),
                    "stock": stock,
                    "is_active": True,
                },
            )
            products.append(product)

        cart_count = 0
        cart_item_count = 0
        for user in users:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_count += 1
            selected_products = rng.sample(products, k=3)
            for product in selected_products:
                CartItem.objects.update_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": rng.randint(1, 4)},
                )
                cart_item_count += 1

        statuses = ["PENDING", "CONFIRMED", "DELIVERED", "CONFIRMED", "PENDING"]
        order_count = 0
        order_item_count = 0
        for number, user in enumerate(users[:5], start=1):
            selected_products = rng.sample(products, k=3)
            lines = [(product, rng.randint(1, 3)) for product in selected_products]
            subtotal, tax_amount, grand_total = calculate_totals(lines)
            address = f"SEED TEST ADDRESS {number} - Do not ship"
            phone = f"+9199000000{number:02d}"

            order, _ = Order.objects.get_or_create(
                user=user,
                address=address,
                phone=phone,
                defaults={
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "grand_total": grand_total,
                    "status": statuses[number - 1],
                    "city": "Test City",
                    "state": "Test State",
                    "zip_code": "110001",
                },
            )

            # Keep the order totals aligned with the demo order lines on reruns.
            order.subtotal = subtotal
            order.tax_amount = tax_amount
            order.grand_total = grand_total
            order.status = statuses[number - 1]
            order.city = "Test City"
            order.state = "Test State"
            order.zip_code = "110001"
            order.save()

            for product, quantity in lines:
                OrderItem.objects.update_or_create(
                    order=order,
                    product=product,
                    defaults={
                        "quantity": quantity,
                        "price": product.price,
                        "total_price": money(product.price * quantity),
                    },
                )
                order_item_count += 1
            order_count += 1

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"Users available: {len(users)}")
        self.stdout.write(f"Products available: {len(products)}")
        self.stdout.write(f"Carts processed: {cart_count}; cart items processed: {cart_item_count}")
        self.stdout.write(f"Orders processed: {order_count}; order items processed: {order_item_count}")
        self.stdout.write(f"Demo login password for newly created users: {SEED_PASSWORD}")
        self.stdout.write("Emails: customer01@example.com through customer08@example.com")

from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()



class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart({self.user})"
    
    @property
    def subtotal(self):
        subtotal = Decimal("0.00")
        for item in self.items.all():
            subtotal += item.product.price * item.quantity
        return subtotal
    
    @property
    def tax_amount(self):
        tax = Decimal("0.00")
        for item in self.items.all():
            tax = tax + item.product.price * item.quantity * Decimal(item.product.tax_percent) / Decimal("100")
        return tax
    
    @property
    def grand_total(self):
        grand_total = self.subtotal + self.tax_amount
        return grand_total.quantize(Decimal("0.00"))


    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        total_price = self.product.price * self.quantity
        return total_pricefrom decimal import Decimal
from django.db import models



class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2) # 200.00
    stock = models.PositiveIntegerField()
    tax_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.namefrom django.db import models
from django.contrib.auth import get_user_model
from products.models import Product


User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('DELIVERED', 'Delivered')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# AbstractUser = add/modify any fields.
# AbstractBaseUser = we use this if you want to get the full control over your user model
# BaseUserManager = Employee.objects = Manager


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email" # you can login with email address
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

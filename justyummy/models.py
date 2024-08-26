from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
import uuid
from datetime import datetime
from .custusermanager import CustomUserManager
from django.utils import timezone

class ProductCategory(models.TextChoices):
    PHONES = "phone", "Phone"
    COMPUTER = "computer", "Computer"
    SMARTWATCH = "wristwatch", "Wristwatch"
    CAMERA = "camera", "Camera"
    HEADPHONES = "headphone", "Headphone"
    GAMING = "gaming", "Gaming"
    SHOE = "shoe, shoe"
    JEWERLRY = "jewelry", "Jewelry"
    CLOTHE = "clothe", "Clothe"
    PERFUME = "perfume", "Perfume"
    NECKLACE = "necklace", "Necklace"
    ELECTRONIC = "electronic", "Electronic"
    TOY = "toy", "Toy"
    NONE = "none", "None"


class ProductDesignation(models.TextChoices):
    MEN = "men", "Men"
    WOMEN = "women", "Women"
    BOTH = "both", "Both"
    CHILDREN = 'children', "Children"
    BABY = "baby", "Baby"
    ALL = "all", "All"

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    groups = models.ManyToManyField(Group, related_name="user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_set", blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class Product(models.Model):
    productId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productName = models.CharField(max_length=64, null=False)
    productCategory = models.CharField(max_length=32, unique=True, choices=ProductCategory.choices, default=ProductCategory.NONE)
    isOnFlashSale = models.BooleanField(default=False)
    productprice = models.IntegerField(default=0)
    flashSalePrice = models.IntegerField(default=0)
    isBestSelling = models.BooleanField(default=False)
    orderRate = models.IntegerField(default=0)
    productDesignation = models.CharField(max_length=32, unique=True, choices=ProductDesignation.choices, default=ProductDesignation.ALL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

class CustomerBillingDetails(models.Model):
    billingDetailId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_at = models.DateField(auto_now_add=True)
    first_name = models.CharField(max_length=64)
    company_name = models.CharField(max_length=64)
    street_name = models.CharField(max_length=64)
    apartment = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=64)
    payment_method = models.CharField(max_length=64)
    payment_type = models.CharField(max_length=64)
    total_price = models.FloatField()

class CustomerReciept(models.Model):
    receiptId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    billing_detail = models.ForeignKey(CustomerBillingDetails, on_delete=models.CASCADE)
    paymentStatus = models.BooleanField(default=False)
    shippingPrice = models.IntegerField(default=0, blank=True, null=True)
    VATOnProduct = models.IntegerField(default=0, blank=True, null=True)
    grandTotalPriceOnProducts = models.FloatField()
    isRefund = models.BooleanField(default=False)

class CustomerOrders(models.Model):
    orderId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orderName = models.CharField(max_length=1024, null=False)
    orderQuantity=models.IntegerField(default=1)
    orderDate = models.DateField(auto_now_add=True)
    orderTotalPrice = models.CharField(null=False, max_length=24)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    receipt = models.ForeignKey(CustomerReciept, on_delete=models.CASCADE)

class Comment(models.Model):
    commentId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=False)
    publishDate = models.DateField(default=timezone.now, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)








from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
import uuid
from datetime import datetime
from .custusermanager import CustomUserManager


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
    productId = models.UUIDField(primary_key=True, auto_created=uuid.uuid4())
    productName = models.CharField(max_length=64, null=False)
    productCategory = models.CharField(max_length=32, unique=True, choices=ProductCategory.choices, default=ProductCategory.NONE)
    isOnFlashSale = models.BooleanField(default=False)
    productprice = models.IntegerField(default=0)
    flashSalePrice = models.IntegerField(default=0)
    isBestSelling = models.BooleanField(default=False)
    orderRate = models.IntegerField(default=0)
    productDesignation = models.CharField(max_length=32, unique=True, choices=ProductDesignation.choices, default=ProductDesignation.ALL)
    created_at = models.DateTimeField(default=datetime.today())
    update_at = models.DateTimeField(default=datetime.today())
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

class CustomerReciept(models.Model):
    receiptId = models.UUIDField(primary_key=True, auto_created=uuid.uuid1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_created=datetime.today().isoformat())
    paymentStatus = models.BooleanField(default=False)
    shippingPrice = models.IntegerField(default=0)
    VATOnProduct = models.IntegerField(default=0)
    grandTotalPriceOnProducts = models.IntegerField(default=0)
    isRefund = models.BooleanField(default=False)

class CustomerPurchasedOrders(models.Model):
    productPurchaseId = models.UUIDField(primary_key=True, auto_created=uuid.uuid3)
    productName = models.CharField(max_length=64)
    quantity=models.IntegerField(default=1)
    purchaseDate = models.DateField(auto_created=datetime.today().isoformat())
    productPriceTotal = models.IntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    receipt = models.ForeignKey(CustomerReciept, on_delete=models.CASCADE)


class Comment(models.Model):
    commentId = models.UUIDField(primary_key=True, auto_created=uuid.uuid4)
    text = models.TextField(null=False)
    publishDate = models.DateField(auto_created=datetime.today())
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Clock(models.Model):
    expiration_date = models.DateField()



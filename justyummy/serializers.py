from rest_framework.serializers import ModelSerializer
from .models import *


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
                continue
            setattr(instance, key, value)
        instance.save()
        return instance
    
class CustomerReceiptSerializer(ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = CustomerReciept
        fields = '__all__'
    
    def create(self, validated_date):
        user = validated_date.pop("user")
        user = CustomUser.objects.create(**user)
        reciept = CustomerReciept.objects.create(user=user, **validated_date)
        reciept.save()
        return reciept
        

class ProductSerializer(ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = Product
        fields = "__all__"
    
    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        product.save()
        return product

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class CustomerPurchasedOrderSerializer(ModelSerializer):
    user = CustomUserSerializer()
    receipt = CustomerReceiptSerializer()
    class Meta:
        model = CustomerPurchasedOrders
        fields = "__all__"

    def create(self, validated_data):
        purchasedOrder = CustomerPurchasedOrders.objects.create( **validated_data)
        purchasedOrder.save()
        return purchasedOrder


class ClockSerializer(ModelSerializer):
    class Meta:
        models = Clock
        fields = "__all__"
        
    def create(self, validated_data):
        clock = Clock.objects.create(**validated_data)
        clock.save()
        return clock
    


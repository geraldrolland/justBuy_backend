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


class CustomerBillingDetailsSerializer(ModelSerializer):
    class Meta:
        model =  CustomerBillingDetails #CustomerBillingDetails
        fields = "__all__"
    
    def create(self, validated_data):
        # You can remove the print statement if not needed
        print("worked")
        billing_details = CustomerBillingDetails.objects.create(**validated_data)
        return billing_details
    
class CustomerReceiptSerializer(ModelSerializer):
    class Meta:
        model = CustomerReciept
        fields = "__all__"
    
    def create(self, validated_data):
        receipt = CustomerReciept.objects.create(**validated_data)
        return receipt


class CustomerOrderSerializer(ModelSerializer):
    class Meta:
        model = CustomerOrders
        fields = "__all__"

    def create(self, validated_data):
        print(" is order working")
        customerOrder = CustomerOrders.objects.create(**validated_data)
        customerOrder.save()
        return customerOrder
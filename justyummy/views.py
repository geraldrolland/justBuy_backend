from django.shortcuts import redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.cache  import cache_page, never_cache, cache_control
from django.core.cache import cache
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import *
from .custompermissions import *
import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
import requests
import base64
import uuid
import json
class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def create_user(self, request, format=None):
        print(request.data)

        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login_user(self, request, format=None):
        user = get_object_or_404(CustomUser, email=request.data.get("email"))
        if user.check_password(request.data.get("password")):
            refresh = RefreshToken.for_user(user=user)
            print(user.email)
            return Response({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response({"detail": "incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)       


    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["get"])
    def get_user(self, request, format=None):
        user = CustomUser.objects.filter(email=request.user.email)
        serializer = CustomUserSerializer(user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[AllowAny], methods=["post"])
    def get_otp(self, request, format=None):
        print(request.data.get("email"))
        print("error")
        otp = random.randint(5101, 8963)
        print("this is my cookies otp to hash", otp)
        otp_str = UserViewSet.otp_hash_algo(otp)
        print(otp_str)
        response = JsonResponse({"detail": "otp created successfully"},  status=status.HTTP_201_CREATED)
        response.set_cookie(key="otp", value=otp_str, path="/users/verify_otp/", domain="localhost:8000", samesite="lax", max_age=3600, httponly=False, secure=False)
        #response.set_cookie("email", request.data.get("email"), max_age=3600, httponly=False, secure=False)
        print(response.cookies)
        subject = "User Change Password"
        html_content = '''
        <html><body style="color: gray"> 
        <div style="color:white, margin-bottom: 5px; width: 100%;">Dear Sir / Madam,</div>
<div >To complete your recent request, please use the following One-Time Password (OTP):

<span style="color: blue; display: block; margin-top: 10px; margin-bottom: 10px">{}</span>

<div style="margin-bottom: 15px; width: 100%">This OTP is valid for the next <span style="color:white">2 minutes</span>. For security reasons, do not share this code with anyone.</div>

<div style="margin-bottom: 15px; width: 100%">If you did not request this code, please contact our support team immediately at <span style="color: green;">{}</span> or <span style="color:green;">+2349050894145</span>.

<div style="margin-bottom: 15px; width: 100%">Thank you for using [Your Company's Name].</div>

<div style="margin-bottom: 15px; width: 100%">Best regards,</div>

<div><span style="font-size: 35px; width: 100%;">justBuy</span> Support Team</div>
        </body></html>
        '''.format(otp, settings.EMAIL_HOST_USER)
        mail_from = settings.EMAIL_HOST_USER
        receipient = [request.data.get("email")]
        email = EmailMessage(subject, html_content, mail_from, receipient)
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        return response

    @action(detail=False, permission_classes=[AllowAny], methods=["post"])
    def verify_otp(self, request, format=None):
        print("this is the cookie otp to unhash", request.COOKIES.get("otp"))
        try:
            print(UserViewSet.otp_unhash_algo(request.COOKIES.get("otp")))
            print(type(UserViewSet.otp_unhash_allgo(request.COOKIES.get("otp"))))
            print(request.data.get("otp"))
            print(type(request.data.get("otp")))
            if request.data.get("otp") == UserViewSet.otp_unhash_algo(request.COOKIES.get("otp")):
                response = Response({"detail": "otp verified successfully"}, status=status.HTTP_200_OK)
                response.set_cookie('permitChangePasswd', True, httponly=True)
                return response
            return Response({"detail": "invalid otp"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except KeyError as e:
            return Response({"detail": "incorrect otp"}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, permission_classes=[AllowAny], methods=["post"])
    def change_user_password(self, request, format=None):
        try:
            if request.user.IsAuthenticated():
                user = CustomUser.objects.filter(email=request.user.get("email"))
                serializer = CustomUserSerializer(user, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"detail": "password changed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            if request.COOKIES.get("permitChangePasswd") == 'True':
                user_email = request.COOKIES.get("email")
                user = get_object_or_404(CustomUser, email=user_email)
                request.data["email"] = user_email
                serializer = CustomUserSerializer(user, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response = Response({"detail": "password changed succesfully"}, status=status.HTTP_200_OK)
                response.delete_cookie("email")
                response.delete_cookie("permitChangePasswd")
                return response
            return Response({"detail": "bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["post"])
    def update_user(self, request, format=None, pk=None):
        user = get_object_or_404(CustomUser, id=pk)
        serializer = CustomUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["delete"])
    def delete_user(self, request, format=None, pk=None):
        user = get_object_or_404(CustomUser, id=pk)
        user.delete()
        return Response({"detail": "user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[BasicAuthentication, SessionAuthentication, JWTAuthentication], methods=["post"])    
    def logout_user(self, request, format=None):
        request.method = "Post"
        return redirect("/token-blacklist")

    @action(detail=False, permission_classes=[IsAuthenticated, IsAdminPermission], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["post"])
    def create_staff(self, request, format=None):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = CustomUser.objects.filter(email=request.data.get("email"))
        user.is_staff = True
        user.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    
        
    @action(detail=True, permission_classes=[IsAuthenticated, IsStaffPermission, IsAdminPermission], authentication_classes=[JWTAuthentication, BasicAuthentication, SessionAuthentication], methods=["post"])
    def update_staffOrAdmin(self, request, format=None, pk=None):
        user = CustomUser.objects.filter(id=pk)
        serializer = CustomUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated, IsAdminPermission], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication])
    def delete_staff(self, request, format=None, pk=None):
        user = CustomUser.objects.filter(id=pk)
        user.is_staff = False
        user.save()
        return Response({"detail": "staff deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def otp_hash_algo(otp):
        otp_str = str(otp)
        hash_map_dict = {
        '0': '}?<%', '1': '*\\)>',
        '2': '/$<?', '3': '/($?',
        '4': '!$@<', '5': ']..$',
        '6': '@){:', '7': ']:,$', 
        '8': '],)/', '9': '>*!&'
        }
        hash_str = ""
        i = 0
        for ch in otp_str:
            hash_str += hash_map_dict[ch]
            if i != 3:
                hash_str += "="
            i += 1
        return hash_str
        
    @staticmethod
    def otp_unhash_algo(hash_str):
        if hash_str is None:
            print("hash_str is none")
        print(hash_str)
        unhash_map_dict = {
            '}?<%': "0", '*\\)>': "1",
            '/$<?': "2", '/($?': "3",
            '!$@<': "4", ']..$': "5",
            '@){:': "6", ']:,$': "7",
            '],)/': "8", '>*!&': "9"
        }
        otp_str = ""
        hash_str = hash_str.split("=")
        print("this is the hash str list", hash_str)
        for _str in hash_str:
            otp_str += unhash_map_dict[_str]
        otp = int(otp_str)
        print("this is the unhash otp", otp)
        return otp

class ProductViewSet(viewsets.ViewSet):
    @action(detail=False, permission_classes=[IsAuthenticated, IsAdminPermission], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["post"])
    def create_product(self, request, format=None):
        user = get_object_or_404(CustomUser, email=request.user.email)
        request_data = request.data.copy()
        request_data["user"] = user.id
        serializer = ProductSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, permission_classes=[IsAdminPermission, IsAuthenticated], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["post"])
    def update_product(self, request, format=None, pk=None):
        product = get_object_or_404(Product, productId=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    

    @action(detail=True, permission_classes=[IsAdminPermission, IsAuthenticated], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["delete"])
    def delete_product(self, request, format=None, pk=None):
        product = get_object_or_404(Product, productId=pk)
        product.delete()
        return Response({"detail": "product deleted succesfully"}, status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False, permission_classes=[AllowAny])
    def get_all_product(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, permission_classes=[AllowAny], methods=["get"])
    def get_productdetail(self, request, format=None, pk=None):
        product = get_object_or_404(Product, productId=pk)
        serializer = ProductSerializer(product)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def get_product_onflashsales(self, request, format=None):
        products = Product.objects.filter(onFlashSale=True)
        serializer = ProductSerializer(products, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def get_products_by_category(self, request, format=None):
        products = Product.objects.filter(ProductCategory=request["GET"]["ProductCategory"])
        serializer = ProductSerializer(products, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, permission_classes=[AllowAny], methods=["get"])
    def get_products_by_designation(self, request, format=None):
        products = Product.objects.filter(ProductCategory=request["GET"]["productCategory"], ProductDesignation=request["GET"]["ProductDesignation"])
        serializer = ProductSerializer(products, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PurchasedProduct(viewsets.ViewSet):
    pass
    

class ProcessCustomerPayment(viewsets.ViewSet):

    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, BasicAuthentication, SessionAuthentication], methods=["post"])
    def create_order(self, request, format=None):
        orders = request.data.get("orders")
        billing_details = request.data.get("billing_details")
        print(billing_details)
        print(orders)
        billing_detail = CustomerBillingDetailsSerializer(data=billing_details)
        billing_detail.is_valid(raise_exception=True)
        billing_detail.save()
        print(billing_detail.data["billingDetailId"])
        user = get_object_or_404(CustomUser, email=request.user.email)
        billing_detail = get_object_or_404(CustomerBillingDetails, billingDetailId=billing_detail.data["billingDetailId"])
        print(billing_detail.billingDetailId)
        print(user.id)
        receipt = {"user": user.id, "billing_detail": billing_detail.billingDetailId, "grandTotalPriceOnProducts": billing_detail.total_price, "isRefund": False, "paymentStatus": False, "shippingPrice": 10, "VATOnProduct": 10}
        print(receipt)
        receipt = CustomerReceiptSerializer(data=receipt)
        print("receipt")
        receipt.is_valid(raise_exception=True)
        receipt.save()
        print("error1")
        order_list = []
        print(receipt.data["receiptId"])
        for order in orders:

            print("order")
            customerOrder = {
                "orderName": order["title"],
                "orderQuantity": order["quantity"],
                "orderTotalPrice": str(order["subTotal"]),
                "user": user.id,
                "receipt": receipt.data["receiptId"],
            }

            customerOrder = CustomerOrderSerializer(data=customerOrder)
            customerOrder.is_valid(raise_exception=True)
            print(customerOrder.initial_data)
            customerOrder.save()
            order_list.append(customerOrder)
        payment_method = request.data["billing_details"]["payment_method"]
        if payment_method == "bank":
            payment_type = request.data["billing_details"]["payment_type"]
            if payment_type == "paypal":
                    client_id = "AayoEynirKMLbcu2lyCPdIfUrgfEaWfcDwVYeD8idFL268xmuSKAG1ANvdEEB_CpWVNli9IZRmEiQqVT"
                    client_secret = "EGMT1_At9JQ0oJ8p6rFdM1f74bPzZdHboOWwATcQB9oqYIXc0H7epaZeAFiCO1-oHpIcRMuuj3LnNNNz"
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": "Basic {0}".format(base64.b64encode((client_id + ":" + client_secret).encode()).decode())
                    }
                    response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", data={"client_id": client_id, "client_secret": client_secret,  "grant_type":"client_credentials"}, headers=headers)
                    response = response.json()
                    access_token = response["access_token"]
                    print(access_token)
                    headers = {
                        "Authorization": "Bearer " + str(access_token),
                        "Content-Type": "application/json",
                        "PayPal-Request-Id": str(uuid.uuid4())
                    }
                    body = {
                        "intent": "CAPTURE",
                        "purchase_units": [
                            {
                                "reference_id": str(uuid.uuid4()),
                                "amount": {
                                    "currency_code": "USD",
                                    "value": "100.00"
                                },
                                "shipping": {
                                    "address": {
                                        "address_line_1": "2211 N First Street",
                                        "address_line_2": "Building 17",
                                        "admin_area_2": "San Jose",
                                        "admin_area_1": "CA",
                                        "postal_code": "95131",
                                        "country_code": "US"
                                    }
                                }
                            }
                        ],
                        "payment_source": {
                            "paypal": {
                                "experience_context": { 
                                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED", 
                                    "brand_name": "justBuy", 
                                    "locale": "en-US", 
                                    "landing_page": "LOGIN", 
                                    "shipping_preference": "SET_PROVIDED_ADDRESS", 
                                    "user_action": "PAY_NOW", 
                                    "return_url": "http://127.0.0.1:8000/customer-order/paypal_return_url/", 
                                    "cancel_url": "http://127.0.0.1:8000/customer-order/paypal_cancel_url/" 
                                }
                            }
                        }
                    }
                    url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'
                    response = requests.post(url, json=body, headers=headers)
                    if response.status_code == 200:
                        order_id = response.json()["id"]
                        payment_url =  response.json()["links"][1]["href"]
                        request.session["order_id"] = order_id
                        response = Response({
                            "detail": "order created succesfully", 
                            "link": payment_url
                            }, status=status.HTTP_201_CREATED)
                        return  response
                    response = response.json()
                    print(response["details"][0])
                    return Response(status=400)
            
            elif payment_method == "mastercard":
                pass

            elif payment_method == "visa":
                pass

            elif payment_method == "stripe":
                pass

    @action(detail=False, permission_classes=[AllowAny], authentication_classes=[BasicAuthentication, SessionAuthentication])
    def paypal_return_url(self, request, format=None):
        return Response({"detail": "payment completed succesfully"}, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, BasicAuthentication, SessionAuthentication])
    def paypal_cancel_url(self, request, format=None):
        return Response({"detail": "order canceled"}, status=status.HTTP_400_BAD_REQUEST)
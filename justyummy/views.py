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
            return Response({
                "id": user.id,
                "email": user.email,
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
        otp_str = UserViewSet.otp_hash_algo(otp)
        print(otp_str)
        response = Response({"detail": "otp created successfully"},  status=status.HTTP_201_CREATED)
        response.set_cookie("otp", otp_str, max_age=360000)
        response.set_cookie("email", request.data.get("email"))
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
        email.send()
        return response

    @action(detail=False, permission_classes=[AllowAny], methods=["post"])
    def verify_otp(self, request, format=None):
        print(request.COOKIES.get("otp"))
        """
        try:
            if request.data.get("otp") == UserViewSet.otp_unhash_algo(request.COOKIES.get("otp")):
                response = Response({"detail": "otp verified successfully"}, status=status.HTTP_200_OK)
                response.set_cookie('permitChangePasswd', True, secure=True)
                return response
        except KeyError as e:
            return Response({"detail": "incorrect otp"}, status=status.HTTP_400_BAD_REQUEST)
            """
        return Response({"detail Cookies printed"}, status=status.HTTP_200_OK)
    
    @action(detail=False, permission_classes=[AllowAny], methods=["post"])
    def change_user_password(self, request, format=None):
        if request.user.IsAuthenticated:
            user = CustomUser.objects.filter(email=request.user.get("email"))
            serializer = CustomUserSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "password changed successfully"}, status=status.HTTP_200_OK)
        if request.COOKIES.get("permitChangePasswd") == True:
            user_email = request.COOKIES.get("email")
            user = get_object_or_404(CustomUser, email=user_email)
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
        for ch in otp_str:
            hash_str += hash_map_dict[ch]
            if ch != otp_str[3]:
                hash_str += "="
        return hash_str
        
    @staticmethod
    def otp_unhash_algo(hash_str):
        if hash_str is None:
            print("hash_str is none")
            return 1256
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
        for _str in hash_str:
            otp_str += unhash_map_dict[_str]
        otp = int(otp_str)
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
    




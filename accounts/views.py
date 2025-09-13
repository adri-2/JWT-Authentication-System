from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserLoginSerializer,SetNewPasswordSerializer,PasswordResetRequestSerializer,LogoutSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user
from .models import OneTimePassword, User
from rest_framework.permissions import IsAdminUser,IsAuthenticated

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str,DjangoUnicodeDecodeError,force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Create your views here.

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self,request): 
        user_data=request.data
        serializer=self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            #send email funct
            send_code_to_user(user['email'])
            return Response({
                'data':user,
                'message':f'hi {user["first_name"]} thanks for signing up a passcode'
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class VerifyUserView(APIView):
    def post(self,request):
        otpcode=request.data.get('otp')
        try:
            user_code_obj =OneTimePassword.objects.get(code=otpcode)
            user =user_code_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':f'hi  thanks for verifying your account'
                },status=status.HTTP_200_OK)
            return Response({
                'message':f'hiyour code {otpcode} is already verified'
            },status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({
                'error':'Invalid OTP code'
            },status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class= UserLoginSerializer
    def post(self,request):
        serializer=self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class TestAuthenticationView(GenericAPIView):
    
    permission_classes =[IsAdminUser]

    def get(self,request):
        data={
            'msg':'its works'
        }
        return Response(data,status=status.HTTP_200_OK)
    

class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self,request):
        serializer=self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({"message":"a link has been set to your email to "},status=status.HTTP_200_OK)
    
class PasswordResetConfirm(GenericAPIView):
    def get(self,request,uidb64,token):
        try:
            user_id=force_bytes(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({"message":"token is invalid or has expired"},status=status.HTTP_401_UNAUTHORIZED)
            return Response({'succes':True,'message':'credentials is valid','uidb64':uidb64,'token':token},status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({"message":"token is invalid or has expired"},status=status.HTTP_401_UNAUTHORIZED)
        
class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self,request):      
        serializer=self.serializer_class(data=request.data)  
        serializer.is_valid(raise_exception=True)
        return Response({'message':'password reset successfull'},status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    serializer_class=LogoutSerializer
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'logout successful'},status=status.HTTP_204_NO_CONTENT)
from re import I
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from django.core.validators import MinLengthValidator
from .validators import number_validator, special_char_validator, letter_validator
from django_rest_ecommerce_project.users.models import BaseUser , Profile
from django_rest_ecommerce_project.api.mixins import ApiAuthMixin
from django_rest_ecommerce_project.users.selectors import get_profile, get_user, get_all_users
from django_rest_ecommerce_project.users.services import register 
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField
from drf_spectacular.utils import extend_schema


class ProfileApi(ApiAuthMixin, APIView):

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile 
            fields = ("user",)

    @extend_schema(responses=OutPutSerializer)
    def get(self, request):
        
        query = get_profile(user=request.user)
        return Response(self.OutPutSerializer(query, context={"request":request}).data)


class RegisterApi(APIView):


    class InputRegisterSerializer(serializers.Serializer):
        first_name = serializers.CharField(max_length=225)
        last_name = serializers.CharField(max_length=225)
        email = serializers.EmailField(max_length=255)
        phone = PhoneNumberField()
        address = serializers.CharField(max_length=500, required=False, allow_blank=True) 
        password = serializers.CharField(
                validators=[
                        number_validator,
                        letter_validator,
                        special_char_validator,
                        MinLengthValidator(limit_value=10)
                    ]
                )
        confirm_password = serializers.CharField(max_length=255)
        
        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email 
        def validate_phone(self, phone):
            if BaseUser.objects.filter(phone=phone).exists():
                raise serializers.ValidationError("phone number Already Taken") 
            return phone 

        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")
            
            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data


    class OutPutRegisterSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = ("id", "first_name", "last_name", "phone", "email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data


    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                    email=serializer.validated_data.get("email"), #type: ignore
                    password=serializer.validated_data.get("password"),#type: ignore
                    phone=serializer.validated_data.get("phone"),#type: ignore
                    address = serializer.validated_data.get("address"),#type: ignore
                    first_name=serializer.validated_data.get("first_name"), #type: ignore
                    last_name=serializer.validated_data.get("last_name")#type: ignore
                    
                    
            ) 
        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data) 
    def get(self, request, pk=None):
        if pk: 
            user = get_user(pk=pk) 
            if isinstance(user, Response):
                return user
            return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data)
            
        users = get_all_users()
        return Response(self.OutPutRegisterSerializer(users, many=True, context={"request":request}).data)
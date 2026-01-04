from rest_framework.views import APIView
from rest_framework.response import Response 
from django_rest_ecommerce_project.orders.models import (Order, OrderItem,
                                                         Payment, Discount
                                                         )
from rest_framework import status 
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField 
from drf_spectacular.utils import extend_schema
from django_rest_ecommerce_project.users.selectors import get_profile 
from django_rest_ecommerce_project.orders.selectors import get_all_orders_by_customer
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from django_rest_ecommerce_project.cart.models import Cart
from django_rest_ecommerce_project.users.selectors import get_profile


class OutputOrderItemSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source="product.name",
                                         read_only=True)
    product_slug = serializers.SlugField(source="product.slug",
                                         read_only=True)
    total_items = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_slug",
            "quantity",
            "total_items",
            "created_at"
        )
    def get_total_price_item(self, obj):
        return obj.get_total_price_item() 

class OutputPaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payment
        fields = (
            "id",
            "payment_id",
            "authority",
            "amount",
            "gateway",
            "status",
            "ref_id",
            "transaction_id",
            "created_at"
        )

class OutputOrderSerializer(serializers.ModelSerializer): 
    items = OutputOrderItemSerializer(source="orderitems",
                                      read_only=True) 
    customer_email = serializers.EmailField(source="customer.user.email",
                                            read_only=True)
    customer_phone = PhoneNumberField(source="customer.user.phone",
                                      read_only=True)
    total_amount = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    
    class Meta:
        model = Order 
        fields = (
            "id",
            "customer_email",
            "customer_phone",
            "items",
            "total_price",
            "total_items",
            "status",
            "payment_status",
            "payment_gateway",
            "tracking_number",
            "shipping_address",
            "billing_address",
            "shipping_method",
            "shipping_cost",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "payment",
            "created_at",
            "updated_at"
        )
    
    def get_total_amount(self,obj):
        return obj.get_total_amount() 
    def get_payment(self,obj):
        try:
            payment = obj.payment
            return OutputPaymentSerializer(payment).data 
        except:
            return None 

class OrderListApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    class InputCreateOrderSerializer(serializers.Serializer):
        
        shipping_method_choices = serializers.ChoiceField(choices=['standard', 
                                                                   'express', 
                                                                   'overnight', 
                                                                   'pickup'],
                                                          default='standard'
                                                          )
        discount_code = serializers.CharField(required=False,
                                          allow_blank=True, 
                                          max_length=50) 
    
    @extend_schema(responses=OutputOrderSerializer(many=True))
    def get(self, request):
        customer = get_profile(user=request.user) 

        orders = get_all_orders_by_customer(customer=customer)
        if not orders:
            return Response({"error":"not found any orders for you."},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = OutputOrderSerializer(orders, many=True, 
                                           context={"request":request}) 
        return Response(serializer.data) 
    
         
        
        
            
            
        
        
        
    
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    

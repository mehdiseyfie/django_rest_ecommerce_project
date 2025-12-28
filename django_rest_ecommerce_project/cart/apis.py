from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django_rest_ecommerce_project.cart.models import Cart, CartItem 
from drf_spectacular.utils import extend_schema 
from django_rest_ecommerce_project.products.models import Product
from django_rest_ecommerce_project.cart.selectors import get_cart_by_slug, get_cart_by_customer, get_cart_item_by_id
from rest_framework import status
from django_rest_ecommerce_project.cart.services import get_or_create_cart, add_item_to_cart, update_cart_item, remove_item_from_cart
from rest_framework.permissions import IsAuthenticated 
from django_rest_ecommerce_project.users.selectors import get_profile
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache


class OutputCartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items in output"""
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.SlugField(source="product.slug", read_only=True)
    product_image = serializers.ImageField(source="product.product_images.image", read_only=True)
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_slug",
            "product_image",
            "quantity",
            "price",
            "item_total",
            "created_at"
        ) 
        
    def get_item_total(self, obj):
        return obj.get_total_price_item()


class OutputCartSerializer(serializers.ModelSerializer):
    """Serializer for cart in output"""
    items = OutputCartItemSerializer(source="cartitems",
                                     many=True,
                                     read_only=True
                                     )
    customer_email = serializers.EmailField(source="customer.user.email", 
                                            read_only=True
                                            )
    
    class Meta:
        model = Cart 
        fields = (
            "id",
            "slug",
            "customer_email",
            "total_price",
            "total_items",
            "is_active",
            "is_ordered",
            "items",
            "created_at",
            "updated_at"
        )


class CartApi(APIView):
    """API for retrieving cart details"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
            
    @extend_schema(responses=OutputCartSerializer)
    def get(self, request, slug=None):
        """Get customer's cart or cart by slug"""
        customer = get_profile(user=request.user)
        
        if slug:
            cart = get_cart_by_slug(slug=slug)
            if cart.customer != customer:
                return Response(
                    {"error": "You don't have access to this cart."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            cart = get_cart_by_customer(customer=customer)
            if not cart:
                cart = get_or_create_cart(customer=customer) 
        cache.set(f"cart-{cart.slug}", cart, 3600)
                
        serializer = OutputCartSerializer(cart, context={"request": request})
        return Response(serializer.data)

class CartItemApi(APIView):
    """API for adding items to cart"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    class InputAddItemSerializer(serializers.Serializer):
        product = serializers.SlugRelatedField(
            queryset=Product.objects.all(),
            slug_field="slug"
        )
        quantity = serializers.IntegerField(min_value=1, default=1)
    
    @extend_schema(
        request=InputAddItemSerializer,
        responses=OutputCartItemSerializer
    )
    def post(self, request):
        """Add item to cart"""
        customer = get_profile(request.user)
        serializer = self.InputAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try:
            cart = get_or_create_cart(customer=customer)
            cart_item = add_item_to_cart(
                cart=cart,
                product=validated_data["product"],  # type: ignore
                quantity=validated_data.get("quantity", 1),  # type: ignore
            )
        except Exception as ex:
            return Response(
                {"error": str(ex)},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        serializer = OutputCartItemSerializer(
            cart_item,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailApi(APIView):
    """API for updating/deleting specific cart items"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    class InputItemUpdateSerializer(serializers.Serializer):
        quantity = serializers.IntegerField(min_value=1)
    
    @extend_schema(
        request=InputItemUpdateSerializer,
        responses=OutputCartItemSerializer
    )
    def patch(self, request, item_id):
        """Update cart item quantity"""
        customer = get_profile(request.user) 
        serializer = self.InputItemUpdateSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data 
        
        try:
            cart = get_cart_by_customer(customer=customer)
            if not cart:
                return Response(
                    {"error": "Cart not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            cart_item = get_cart_item_by_id(cart=cart, item_id=item_id) 
            cart_item = update_cart_item(
                cart_item=cart_item,
                quantity=validated_data["quantity"]  # type: ignore
            ) 
        except Exception as ex:
            return Response(
                {"error": str(ex)}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        serializer = OutputCartItemSerializer(
            cart_item,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(responses={204: None})  
    def delete(self, request, item_id):
        """Remove item from cart"""
        customer = get_profile(user=request.user)
        
        try:
            cart = get_cart_by_customer(customer=customer) 
            if not cart:
                return Response(
                    {"error": "Cart not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            cart_item = get_cart_item_by_id(cart=cart, item_id=item_id) 
            remove_item_from_cart(cart_item=cart_item) 
            
        except Exception as ex:
            return Response(
                {"error": str(ex)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    
    
        
        
        
        
        
    
        
        
        

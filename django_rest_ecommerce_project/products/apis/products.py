from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
from rest_framework import serializers
from django_rest_ecommerce_project.products.models import Category, Product
from drf_spectacular.utils import extend_schema
from django_rest_ecommerce_project.products.selectors.products import get_product, get_all_product
from django_rest_ecommerce_project.products.services.products import create_product 



class ProductApi(APIView): 
    class InputProductSerializer(serializers.Serializer):
        category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                                slug_field="slug") 
        name = serializers.CharField(max_length=225)
        description = serializers.CharField(required=False, allow_blank=True) 
        price = serializers.DecimalField(max_digits=10, decimal_places=2) 
        stock = serializers.IntegerField()
        available = serializers.BooleanField() 
        newest_product = serializers.BooleanField() 
        
        def validate_name(self, value):
            if Product.objects.filter(name__exact=value).exists(): 
                raise serializers.ValidationError("A category with this name already exists.") 
            return value 
        
    class OutputProductSerializer(serializers.ModelSerializer):
                
        class Meta: 
            model = Product 
            fields = ("category",
                      "name", 
                      "slug",
                      "description",
                      "price",
                      "stock",
                      "available",
                      "newest_product",
                      )
            read_only_fields = ("slug",) 
            
            
    @extend_schema(responses=OutputProductSerializer(many=True))
    def get(self, request, slug=None):
        if slug:
            product = get_product(slug=slug)
            serializer = self.OutputProductSerializer(product, context={"request":request})
            return Response(serializer.data) 
        
        
        products = get_all_product() 
        serializer = self.OutputProductSerializer(products, many=True, context={"request": request}) 
        return Response(serializer.data) 
    
    @extend_schema(request=InputProductSerializer, responses=OutputProductSerializer)
    def post(self, request): 
        serializer = self.InputProductSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try:
            product = create_product(category=validated_data.get("category"),#type:ignore 
                           name=validated_data.get("name"), #type:ignore
                           description=validated_data.get("description", ""), #type:ignore
                           price=validated_data.get("price"), #type:ignore 
                           stock=validated_data.get("stock"), #type:ignore
                           available=validated_data.get("available", ""), #type:ignore
                           newest_product=validated_data.get("newest_product", ""), #type:ignore
                           )
        except Exception as ex: 
            return Response({"detail": f"Databse error: {str(ex)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response(self.OutputProductSerializer(product, context={"request":request}).data) 

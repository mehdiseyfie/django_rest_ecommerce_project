# products/apis/category.py

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django_rest_ecommerce_project.products.models import Category
from django_rest_ecommerce_project.products.selectors.category import (
    get_all_category, get_category)
from django_rest_ecommerce_project.products.services.category import \
    create_category


class CategoryApi(APIView):
    # Required for handling file uploads (image)
    parser_classes = [MultiPartParser, FormParser]

    class InputCategorySerializer(serializers.Serializer):
        name = serializers.CharField(max_length=225)
        description = serializers.CharField(required=False, allow_blank=True)
        
        image = serializers.ImageField(required=False, allow_null=True)

        def validate_name(self, value):
            if Category.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("A category with this name already exists.")
            return value

    class OutputCategorySerializer(serializers.ModelSerializer):
        # Ensures the full image URL is returned in the response
        image = serializers.ImageField(read_only=True)

        class Meta: 
            model = Category
            fields = ("name", "slug", "description", "image")
           # read_only_fields = ("slug",)

    # GET: List all categories or retrieve a single category by slug
    @extend_schema(responses=OutputCategorySerializer(many=True))
    def get(self, request, slug=None):
        if slug:
            # Raises 404 automatically if not found (thanks to get_object_or_404 in selector)
            category = get_category(slug=slug)
            serializer = self.OutputCategorySerializer(category, context={"request": request})
            return Response(serializer.data)

        # List all categories
        categories = get_all_category()
        serializer = self.OutputCategorySerializer(categories, many=True, context={"request": request})
        return Response(serializer.data)

    # POST: Create a new category
    @extend_schema(request=InputCategorySerializer, responses=OutputCategorySerializer)
    def post(self, request, slug=None):
        serializer = self.InputCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            category = create_category(
                name=validated_data["name"], #type: ignore
                description=validated_data.get("description", ""), #type: ignore
                image=validated_data.get("image") #type: ignore
            )
        except Exception as ex:
            return Response(
                {"detail": f"Database error: {str(ex)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            self.OutputCategorySerializer(category, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )
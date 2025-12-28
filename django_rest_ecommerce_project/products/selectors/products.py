from django_rest_ecommerce_project.products.models import Product 
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

def get_product(slug:str) -> Product:
    return get_object_or_404(Product, slug=slug) 


def get_all_product() -> QuerySet[Product]:
    return Product.objects.all()
    
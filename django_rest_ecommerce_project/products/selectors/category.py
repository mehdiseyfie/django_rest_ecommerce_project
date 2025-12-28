from django_rest_ecommerce_project.products.models import Category 
from rest_framework.response import Response
from rest_framework import status
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404




def get_category(slug:str) -> Category: 
    return get_object_or_404(Category, slug=slug)
   
    
def get_all_category() -> QuerySet[Category]:
    return Category.objects.all() 




from django.urls import path

from django_rest_ecommerce_project.products.apis.category import CategoryApi
from django_rest_ecommerce_project.products.apis.products import ProductApi

urlpatterns = [
    path("categories/", CategoryApi.as_view(), name="categories-list"),
    path("categories/<slug:slug>/", CategoryApi.as_view(), name="category-detail"),
    path("", ProductApi.as_view(), name="products-list"),
    path("<slug:slug>/", ProductApi.as_view(), name="product-detail"),
]
from django.urls import path 
from django_rest_ecommerce_project.cart.apis import CartApi, CartItemApi, CartItemDetailApi, CartClearApi

urlpatterns = [
    path("items/", CartItemApi.as_view(), name="add-item-to-cart" ),
    path("items/<int:item_id>/", CartItemDetailApi.as_view(), name="cart-item-detail"),
    path("clear-cart/", CartClearApi.as_view(), name="clear-cart"),
    
    path("", CartApi.as_view(), name="cart-detail"),
    path("<slug:slug>/", CartApi.as_view(), name="cart-by-slug"),
]
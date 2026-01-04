from django.urls import path
from django_rest_ecommerce_project.orders.apis import OrderListApi

urlpatterns = [
    path("",OrderListApi.as_view(), name="order-list")
]
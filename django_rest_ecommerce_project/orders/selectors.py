from typing import Optional
from django_rest_ecommerce_project.users.models import Profile
from django_rest_ecommerce_project.orders.models import Order, OrderItem


def get_all_orders_by_customer(customer:Profile) -> Optional[Order]:
    
    try:
        return Order.objects.select_related(
                                            "customer__user",
                                            "cart",
                                            "billing_address").prefetch_related(
                                                "orderitems__product").filter(
                                                customer=customer).latest(
                                                    "-created_at")
    except Order.DoesNotExist:
        return None 
    
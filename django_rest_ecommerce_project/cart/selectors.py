from django_rest_ecommerce_project.cart.models import Cart, CartItem 
from django_rest_ecommerce_project.users.models import Profile
from django.shortcuts import get_object_or_404
from typing import Optional
from django.core.cache import cache


def get_cart_by_slug(slug:str) -> Cart: 
    """ get the cart with slug and push slug in django cache

    Args:
        slug (str): _description_

    Returns:
        Cart: _description_
    """
    
    cache_key = f"cart_{slug}"
    cart = cache.get(cache_key) 
    if cart is None:
        cart = get_object_or_404(Cart.objects.select_related("customer__user").prefetch_related("cartitems__product__category"), slug=slug, is_active=True)
        cache.set(cache_key, cart, 3600) 
    return cart 

def get_cart_by_customer(customer:Profile) -> Optional[Cart]:
    try:
        return Cart.objects.select_related("customer__user").get(customer=customer, is_active=True, is_ordered=False)
    except Cart.DoesNotExist:
        return None
        

def get_cart_item_by_id(cart:Cart, item_id:int) -> CartItem:
        return get_object_or_404(CartItem.objects.select_related("cart__customer__user"), cart=cart, id=item_id)
    
    
    
    

def get_cart_totals(cart:Cart) -> dict:
    
    cache_key = f"cart_totals_{cart.slug}"
    totals = cache.get(cache_key) 
    
    if totals is None: 
        totals = {
            "total_price": cart.total_price,
            "total_items": cart.total_items,
            "items_count": cart.cartitems.count() #type:ignore 
        } 
        cache.set(cache_key, totals, 300) 
    return totals 

    
    
    
    
    
    
    
    
    
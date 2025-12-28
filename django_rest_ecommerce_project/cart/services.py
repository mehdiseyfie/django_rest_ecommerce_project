from django_rest_ecommerce_project.users.models import Profile
from django_rest_ecommerce_project.cart.models import Cart, CartItem 
from django_rest_ecommerce_project.products.models import Product 
from django.db import transaction
from django.core.cache import cache
from decimal import Decimal
from django.core.exceptions import ValidationError

@transaction.atomic()
def get_or_create_cart(customer:Profile) -> Cart:
        cart , created = Cart.objects.get_or_create(customer=customer,
                                                    is_active=True,
                                                    is_ordered=False,defaults={
                                                        "total_price": Decimal("0.00"),
                                                        "total_items": 0
                                                    })
        if created:
            cache.delete(f"cart_{cart.slug}")
        
        return cart 
    
    
@transaction.atomic
def add_item_to_cart(
    cart: Cart,
    product: Product,
    quantity: int = 1
) -> CartItem:
    """
    Add item to cart or update quantity if already exists
    """
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    if product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {product.stock}")
    
    # Check if item already exists in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': quantity,
            'price': product.price
        }
    )
    
    if not created:
        # Update existing item
        old_quantity = cart_item.quantity
        old_price = cart_item.price
        
        new_quantity = old_quantity + quantity
        if new_quantity > product.stock:
            raise ValidationError(f"Insufficient stock. Available: {product.stock}")
        
        cart_item.quantity = new_quantity
        cart_item.price = product.price
        cart_item.save(old_quantity=old_quantity, old_price=old_price)
    
    # Clear cache
    cache.delete(f"cart_{cart.slug}")
    cache.delete(f"cart_totals_{cart.slug}")
    
    return cart_item

@transaction.atomic()
def update_cart_item(cart_item:CartItem, quantity:int) -> CartItem:
    if quantity <= 0:
        raise ValidationError("Quantity must be positive") 
    if cart_item.product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {cart_item.product.stock}")  
    
    old_quantity = cart_item.quantity 
    old_price = cart_item.price 
    
    cart_item.quantity = quantity 
    
    cart_item.save(old_quantity=old_quantity, old_price=old_price)
    
    
    cache.delete(f"cart_{cart_item.cart.slug}")
    cache.delete(f"cart_totals_{cart_item.cart.slug}")
    
    
    return cart_item 


@transaction.atomic()
def remove_item_from_cart(cart_item:CartItem)->None:
    
    cart_slug = cart_item.cart.slug
    cart_item.delete()
    
    cache.delete(f"cart_{cart_slug}")
    cache.delete(f"cart_totals_{cart_slug}")
    
    
    
    
    
    
    

        
        
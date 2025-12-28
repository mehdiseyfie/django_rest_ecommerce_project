from django_rest_ecommerce_project.products.models import Product 

def create_product(*, category:str, name:str, description:str, price:str, stock:str, available:str, newest_product:str) -> Product:
    return Product.objects.create(category=category, name=name, 
                                  description=description, price=price, stock=stock, available=available, newest_product=newest_product) 
    
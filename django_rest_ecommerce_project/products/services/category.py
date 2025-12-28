from django_rest_ecommerce_project.products.models import Category 

def create_category(*, name:str, description:str, image:str) -> Category:
    return Category.objects.create(name=name, description=description, image=image) 

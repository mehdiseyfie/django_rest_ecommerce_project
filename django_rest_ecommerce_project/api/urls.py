from django.urls import include, path

urlpatterns = [
    path("users/", include(("django_rest_ecommerce_project.users.urls", "users"))),
    #path('categories/', include(("django_rest_ecommerce_project.products.urls", "products"))),
    path("products/", include("django_rest_ecommerce_project.products.urls")),
    path("cart/", include("django_rest_ecommerce_project.cart.urls")),
    path("authentication/", include(("django_rest_ecommerce_project.authentication.urls", "authentication"))),
    path("orders/", include("django_rest_ecommerce_project.orders.urls"))
]
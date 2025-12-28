from .models import Profile, BaseUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import QuerySet

def get_user(*, pk: int) -> BaseUser | Response:
    try:
        return BaseUser.objects.get(id=pk) 
    except BaseUser.DoesNotExist:
        return Response({"error":"User not found."}, status=status.HTTP_400_BAD_REQUEST) 

def get_all_users() -> QuerySet[BaseUser]:
    return BaseUser.objects.all() 
        

def get_profile(user:BaseUser) -> Profile:
    try:
        return Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Profile.objects.create(user=user)
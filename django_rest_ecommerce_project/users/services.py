from django.db import transaction 
from .models import BaseUser, Profile


def create_profile(*, user:BaseUser) -> Profile:
    return Profile.objects.create(user=user)

def create_user(*, email:str, password:str, phone:str, address:str|None, first_name:str, last_name:str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, password=password, phone=phone, first_name=first_name, last_name=last_name, address=address) #type:ignore


@transaction.atomic
def register(*, email:str, password:str, phone:str, address:str|None, first_name:str, last_name:str) -> BaseUser:

    user = create_user(email=email, password=password, phone=phone, address=address, first_name=first_name, last_name=last_name)
    create_profile(user=user)

    return user
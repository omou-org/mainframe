from graphene_django.types import DjangoObjectType
from scheduler.models import Session

class SessionType(DjangoObjectType):
    class Meta:
        model = Session

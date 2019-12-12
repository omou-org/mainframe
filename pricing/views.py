from django.shortcuts import render
from pricing.models import Price
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from mainframe.permissions import IsDev, ReadOnly

from pricing.serializers import PriceSerializer


# Create your views here.
class PriceViewSet(viewsets.ModelViewSet):
    """"
    API endpoint that allows prices to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Price.objects.all()
    serializer_class = PriceSerializer


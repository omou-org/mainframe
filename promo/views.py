from rest_framework import viewsets

from promo.models import Promo

from promo.serializers import PromoSerializer


class PromoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited
    """
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

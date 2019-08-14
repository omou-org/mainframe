from rest_framework import viewsets

from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

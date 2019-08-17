from rest_framework import viewsets

from payment.models import (
    Payment,
    SessionPayment
)

from payment.serializers import (
    PaymentSerializer,
    SessionPaymentSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class SessionPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited
    """
    queryset = SessionPayment.objects.all()
    serializer_class = SessionPaymentSerializer

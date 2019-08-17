from django.urls import include, path
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    SessionPaymentViewSet
)

router = routers.DefaultRouter()
router.register(r'student', PaymentViewSet)
router.register(r'session', SessionPaymentViewSet)

urlpatterns = [
    path('', include(router.urls))
]

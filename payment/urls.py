from django.urls import include, path
from rest_framework import routers

from payment.views import (
    PaymentViewSet
)

router = routers.DefaultRouter()
router.register(r'student', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls))
]

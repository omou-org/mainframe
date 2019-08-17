from django.urls import include, path
from rest_framework import routers

from promo.views import PromoViewSet

router = routers.DefaultRouter()
router.register(r'', PromoViewSet)

urlpatterns = [
    path('', include(router.urls))
]

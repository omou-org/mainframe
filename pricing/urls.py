from django.urls import include, path
from rest_framework import routers
from pricing import views

router = routers.DefaultRouter()
router.register(r'', views.PriceViewSet)

urlpatterns = [
    path('', include(router.urls))
]

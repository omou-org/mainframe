from django.urls import include, path
from rest_framework import routers
from pricing import views

router = routers.DefaultRouter()
router.register(r'rule', views.PriceRuleViewSet)
router.register(r'static', views.StaticPriceViewSet)


urlpatterns = [
    path('', include(router.urls))
]

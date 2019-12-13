from django.urls import include, path
from rest_framework import routers
from pricing import views

router = routers.DefaultRouter()
router.register(r'rule', views.PriceRuleViewSet)


urlpatterns = [
    path('', include(router.urls))
]

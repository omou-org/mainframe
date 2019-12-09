from django.urls import include, path
from rest_framework import routers
from scheduler import views

router = routers.DefaultRouter()
router.register(r'session', views.SessionViewSet)

urlpatterns = [
    path('', include(router.urls))
]

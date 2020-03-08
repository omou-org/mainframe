from django.urls import include, path
from rest_framework import routers
from payment import views

router = routers.DefaultRouter()
router.register(r'payment', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('unpaid-sessions/', views.UnpaidSessionsView.as_view()),
]

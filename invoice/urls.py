from django.urls import include, path
from rest_framework import routers
from invoice import views

router = routers.DefaultRouter()
router.register(r"invoice", views.InvoiceViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("unpaid-sessions/", views.UnpaidSessionsView.as_view()),
]

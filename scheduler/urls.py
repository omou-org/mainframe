from django.urls import include, path
from rest_framework import routers
from scheduler import views

router = routers.DefaultRouter()
router.register(r"session", views.SessionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "validate/session/<int:instructor_id>",
        views.SessionScheduleValidation.as_view(),
    ),
    path(
        "validate/course/<int:instructor_id>", views.CourseScheduleValidation.as_view()
    ),
]

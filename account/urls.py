from django.urls import include, path
from rest_framework import routers

from account.views import (
    AdminViewSet,
    StudentViewSet,
    ParentViewSet,
    InstructorViewSet
)

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'students', StudentViewSet)
router.register(r'parents', ParentViewSet)
router.register(r'intructors', InstructorViewSet)

urlpatterns = [
    path('', include(router.urls))
]

from django.urls import include, path
from rest_framework import routers

from account.views import (
    NoteViewSet,
    AdminViewSet,
    StudentViewSet,
    ParentViewSet,
    InstructorViewSet,
    CurrentUserView,
)

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'student', StudentViewSet)
router.register(r'parent', ParentViewSet)
router.register(r'instructor', InstructorViewSet)
router.register(r'note', NoteViewSet)

urlpatterns = [
    path(r'user', CurrentUserView.as_view()),
    path(r'', include(router.urls))
]

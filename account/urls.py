from django.urls import include, path
from rest_framework import routers

from account.views import (
	NoteViewSet,
    AdminViewSet,
    StudentViewSet,
    ParentViewSet,
    InstructorViewSet
)

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'student', StudentViewSet)
router.register(r'parent', ParentViewSet)
router.register(r'instructor', InstructorViewSet)

router.register(r'note', NoteViewSet)

urlpatterns = [
    path('', include(router.urls))
]

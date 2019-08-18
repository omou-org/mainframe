from django.urls import include, path
from rest_framework import routers

from account.views import (
	StudentNoteViewSet,
    ParentNoteViewSet,
    InstructorNoteViewSet,
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

router.register(r'student_note', StudentNoteViewSet)
router.register(r'parent_note', ParentNoteViewSet)
router.register(r'instructor_note', InstructorNoteViewSet)

urlpatterns = [
    path('', include(router.urls))
]

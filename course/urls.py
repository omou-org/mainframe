from django.urls import include, path
from rest_framework import routers
from course import views

router = routers.DefaultRouter()
router.register(r'catalog', views.CourseViewSet)
router.register(r'categories', views.CourseCategoryViewSet)
router.register(r'enrollment', views.EnrollmentViewSet)
router.register(r'catalog_note', views.CourseNoteViewSet)
router.register(r'enrollment_note', views.EnrollmentNoteViewSet)

urlpatterns = [
    path('', include(router.urls))
]

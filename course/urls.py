from django.urls import include, path
from rest_framework import routers
from course import views

router = routers.DefaultRouter()
router.register(r'catalog', views.CourseViewSet)
router.register(r'categories', views.CourseCategoryViewSet)
router.register(r'enrollment', views.EnrollmentViewSet)
router.register(r'session', views.SessionViewSet)

urlpatterns = [
    path('', include(router.urls))
]

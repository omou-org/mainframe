from django.http import JsonResponse

from course.models import Course
from course.models import CourseCategory


def get_catalog(request):
    courses = list(Course.objects.values())
    return JsonResponse({
        "data": courses,
    })


def getCourseCategories(request):
    courseCategories = list(CourseCategory.objects.values())
    return JsonResponse({
        "data": courseCategories
    })

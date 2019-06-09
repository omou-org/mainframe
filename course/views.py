from django.http import JsonResponse

from course.models import Course
from course.models import CourseCategory


def get_catalog(request):
    courses = list(Course.objects.values())
    return JsonResponse({
        "data": courses,
    })


def get_course_categories(request):
    course_categories = list(CourseCategory.objects.values())
    return JsonResponse({
        "data": course_categories
    })

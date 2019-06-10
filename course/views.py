from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from course.models import Course
from course.models import CourseCategory


def get_catalog(request):
    courses = list(Course.objects.values())
    return JsonResponse({
        "data": courses
    })


def get_course_categories(request):
    course_categories = list(CourseCategory.objects.values())
    return JsonResponse({
        "data": course_categories
    })


def get_category_courses(request, category_name):
    course_list = get_list_or_404(Course, course_category=category_name)
    return JsonResponse({
        "data": course_list
    })

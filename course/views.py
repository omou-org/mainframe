from django.shortcuts import get_list_or_404
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


def get_courses_for_category(request, category_id):
    course_list = get_list_or_404(Course, course_category=category_id)
    return JsonResponse({
        "data": course_list
    })

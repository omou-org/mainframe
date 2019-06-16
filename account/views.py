from django.http import JsonResponse

from account.models import (
    Instructor,
    Parent,
    Student,
)


def get_students(request):
    students = list(Student.objects.values())
    return JsonResponse({
        "data": students,
    })

def get_instructors(request):
    instructors = list(Instructor.objects.values())
    return JsonResponse({
        "data": instructors,
    })

def get_parents(request):
    parents = list(Parent.objects.values())
    return JsonResponse({
        "data": parents,
    })

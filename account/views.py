from django.http import JsonResponse

from account.models import Instructor, Student


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

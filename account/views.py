from django.http import JsonResponse
from rest_framework.generics import ListAPIView

from account.models import (
    Instructor,
    Parent,
    Student,
)
from account.serializers import (
    StudentSerializer,
)


class StudentListView(ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

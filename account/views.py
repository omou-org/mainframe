from rest_framework.generics import ListCreateAPIView

from account.models import (
    Student,
)
from account.serializers import (
    StudentSerializer,
)


class StudentListView(ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

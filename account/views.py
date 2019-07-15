from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


from account.models import (
    Admin,
    Student,
    Parent,
    Instructor
)
from account.serializers import (
    AdminSerializer,
    StudentSerializer,
    ParentSerializer,
    InstructorSerializer
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited
    """
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class ParentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows parents to be viewed or edited
    """
    permission_classes = (IsAuthenticated,)
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer


class InstructorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instructors to be viewed or edited
    """
    permission_classes = (IsAuthenticated,)
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class AdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admins to be viewed or edited
    """
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

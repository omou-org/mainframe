from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from account.models import (
    StudentNote,
    ParentNote,
    InstructorNote,
    Admin,
    Student,
    Parent,
    Instructor
)
from account.serializers import (
    StudentNoteSerializer,
    ParentNoteSerializer,
    InstructorNoteSerializer,
    AdminSerializer,
    StudentSerializer,
    ParentSerializer,
    InstructorSerializer
) 

class StudentNoteViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows notes to be created or edited or deleted
    """
    queryset = StudentNote.objects.all()
    serializer_class = StudentNoteSerializer

class ParentNoteViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows notes to be created or edited or deleted
    """
    queryset = ParentNote.objects.all()
    serializer_class = ParentNoteSerializer

class InstructorNoteViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows notes to be created or edited or deleted
    """
    queryset = InstructorNote.objects.all()
    serializer_class = InstructorNoteSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows parents to be viewed or edited
    """
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

class InstructorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instructors to be viewed or edited
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

class AdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admins to be viewed or edited
    """
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

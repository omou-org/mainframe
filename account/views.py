from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from account.models import (
    Note,
    Admin,
    Student,
    Parent,
    Instructor
)
from account.serializers import (
    NoteSerializer,
    AdminSerializer,
    StudentSerializer,
    ParentSerializer,
    InstructorSerializer
) 

class NoteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    #def perform_create(self, serializer):
    #    serializer.save(user_id=self.request.user)

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

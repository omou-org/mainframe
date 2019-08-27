from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json

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

    def list(self, request):
        """
        override list to return notes for specific user
        """
        data = json.loads(request.body)
        user_id = data["user"]
        queryset = self.get_queryset().filter(user__id = user_id)
        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)
   
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

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    InstructorSerializer,
    UserSerializer,
)
from mainframe.permissions import ReadOnly


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def list(self, request):
        """
        override list to return notes for specific user
        """
        user_id = request.query_params.get("user_id", None)
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser | ReadOnly]
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class AdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admins to be viewed or edited
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser | ReadOnly]
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer


class CurrentUserView(APIView):
    """
    Returns current user information
    """
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

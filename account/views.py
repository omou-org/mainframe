from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import (
    AccountNote,
    Admin,
    Student,
    Parent,
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from account.serializers import (
    AccountNoteSerializer,
    AdminSerializer,
    StudentSerializer,
    ParentSerializer,
    InstructorSerializer,
    InstructorAvailablitySerializer,
    InstructorOutOfOfficeSerializer,
    UserSerializer,
)
from mainframe.permissions import ReadOnly, IsDev


class NoteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = AccountNote.objects.all()
    serializer_class = AccountNoteSerializer

    def list(self, request):
        """
        override list to return notes for specific user
        """
        user_id = request.query_params.get("user_id", None)
        queryset = self.get_queryset().filter(user__id=user_id)
        serializer = AccountNoteSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def list(self, request):
        queryset = self.get_queryset()[:100]
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)


class ParentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows parents to be viewed or edited
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

    def list(self, request):
        queryset = self.get_queryset()[:100]
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)


class InstructorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instructors to be viewed or edited
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class InstructorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instructors to be viewed or edited
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = InstructorAvailability.objects.all()
    serializer_class = InstructorAvailablitySerializer

    def list(self, request):
        """
        query by instructor_id
        """
        instructor_id = request.query_params.get("instructor_id", None)
        queryset = self.get_queryset().filter(instructor=instructor_id)
        serializer = InstructorAvailablitySerializer(queryset, many=True)
        return Response(serializer.data)


class InstructorOutOfOfficeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instructors out of office to be added and changed
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = InstructorOutOfOffice.objects.all()
    serializer_class = InstructorOutOfOfficeSerializer


class AdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admins to be viewed or edited
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer


class CurrentUserView(APIView):
    """
    Returns current user information
    """

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

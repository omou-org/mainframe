from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dateutil.parser import parse

from account.models import (
    Note,
    Admin,
    Student,
    Parent,
    Instructor,
    InstructorAvailability,
)
from account.serializers import (
    NoteSerializer,
    AdminSerializer,
    StudentSerializer,
    ParentSerializer,
    InstructorSerializer,
    InstructorAvailablitySerializer,
    UserSerializer,
)

from scheduler.models import Session

from course.modelse import (
    Course,
    Enrollment
)

from mainframe.permissions import ReadOnly, IsDev


class NoteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
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


class StudentValidateViewSet(APIView):
    class QuoteTotalView(APIView): 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request):
        user_id = request.query_params.get("user_id", None)
        type = request.query_params.get("type", None)
        start_time = parse(request.query_params.get("start_time", None))
        end_time = parse(request.query_params.get("end_time", None))
        
        user_courses = set(Enrollment.objects.filter(student = user_id).values('course'))

        
        

        if type == "course":
            start_date = parse(request.query_params.get("start_date", None))
            end_date = parse(request.query_params.get("end_date", None))



        if type == "session":
            date = parse(request.query_params.get("date", None))

            Session.objects.filter(
                course__in = user_courses,
                is_confirmed = True,
                start_datetime__date__eq = date,
                start_datetime__time__le = end_time.time(),
                end_datetime__time__ge = start_time.time(),
                )
            





        '''
        student id (required)
        start time (required)
        end time (required)
        type = "course" or "session" (required)
        a date (conditionally required if validating a session)
        a start date (conditionally required if validating a course)
        an end date (conditionally required if validating a course)
        '''

        

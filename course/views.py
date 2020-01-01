from course.models import EnrollmentNote, CourseNote, Course, CourseCategory, Enrollment
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from course.serializers import (
    EnrollmentNoteSerializer,
    CourseNoteSerializer,
    CourseSerializer,
    CourseCategorySerializer,
    EnrollmentSerializer,
)

from mainframe.permissions import IsDev, ReadOnly


class CourseNoteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = CourseNote.objects.all()
    serializer_class = CourseNoteSerializer

    def list(self, request):
        """
        override list to return notes for specific course
        """
        course_id = request.query_params.get("course_id")
        queryset = self.get_queryset().filter(course__id=course_id)
        serializer = CourseNoteSerializer(queryset, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows course categories to be viewed or edited
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer

    """
    Extra route that gets courses by category id
    /api/courses/categories/<category_id>/course_list
    """
    @action(detail=True, methods=['get'])
    def course_list(self, request, pk=None):
        matching_courses = Course.objects.filter(
            course_category=self.get_object())
        matching_courses_json = CourseSerializer(matching_courses, many=True)
        return Response(matching_courses_json.data)


class EnrollmentNoteViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = EnrollmentNote.objects.all()
    serializer_class = EnrollmentNoteSerializer

    def list(self, request):
        """
        override list to return notes for specific enrollment
        """
        enrollment_id = request.query_params.get("enrollment_id", None)
        queryset = self.get_queryset().filter(enrollment_id=enrollment_id)
        serializer = EnrollmentNoteSerializer(queryset, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows enrollments to be created or edited
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def list(self, request):
        """
        override list to return enrollments by student id or course id
        """
        student_id = request.query_params.get("student_id", None)
        course_id = request.query_params.get("course_id", None)
        queryset = self.get_queryset()
        if student_id:
            queryset = queryset.filter(student__user_uuid=student_id)
        elif course_id:
            queryset = queryset.filter(course=course_id)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

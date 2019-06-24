from course.models import Course, CourseCategory
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from course.serializers import CourseSerializer, CourseCategorySerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows course categories to be viewed or edited
    """
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer

    """
    Extra route that gets courses by category id
    /api/courses/categories/<category_id>/course_list
    """
    @detail_route()
    def course_list(self, requiest, pk=None):
        matching_courses = Course.objects.filter(
            course_category=self.get_object())
        matching_courses_json = CourseSerializer(matching_courses, many=True)
        return Response(matching_courses_json.data)

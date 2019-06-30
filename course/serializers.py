from course.models import Course, CourseCategory
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course

        fields = ('url', 'id', 'subject', 'description', 'instructor', 'tuition', 'room', 'days',
                  'schedule', 'start_date', 'end_date', 'max_capacity', 'course_category')


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory

        fields = ('url', 'id', 'name', 'description')

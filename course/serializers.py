from course.models import Course, CourseCategory, Enrollment
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course

        fields = (
            'id',
            'subject',
            'description',
            'instructor',
            'tuition',
            'room',
            'days',
            'schedule',
            'start_date',
            'end_date',
            'max_capacity',
            'course_category'
        )


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory

        fields = ('id', 'name', 'description')

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment

        fields = (
            'student',
            'course',
        )

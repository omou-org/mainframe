from rest_framework import serializers

from course.models import (
    Course,
    CourseCategory,
    Enrollment,
    Session,
)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course

        fields = (
            'url',
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
            'course_category',
        )


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory

        fields = (
            'url',
            'id',
            'name',
            'description',
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment

        fields = (
            'student',
            'course',
        )


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session

        fields = (
            'id',
            'course',
            'start_date_time',
            'end_date_time',
            'price',
        )

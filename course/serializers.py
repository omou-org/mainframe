from course.models import CourseNote, Course, CourseCategory, Enrollment
from rest_framework import serializers

class CourseNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseNote
        read_only_fields = (
            'id',
            'timestamp',
        )
        write_only_fields = (
            'course',
        )
        fields = (
            'id',
            'course',
            'timestamp',
            'title',
            'body',
            'important',
            'complete',
        )


class CourseSerializer(serializers.ModelSerializer):
    enrollment_list = serializers.SerializerMethodField()

    def get_enrollment_list(self, obj):
        return obj.enrollment_list

    class Meta:
        model = Course

        fields = (
            'id',
            'subject',
            'description',
            'instructor',
            'tuition',
            'room',
            'day_of_week',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'max_capacity',
            'course_category',
            'enrollment_list',
        )

        read_only_fields = (
            'enrollment_list',
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

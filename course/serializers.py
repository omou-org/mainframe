from datetime import datetime

import arrow
from django.db import transaction

from course.models import EnrollmentNote, CourseNote, Course, CourseCategory, Enrollment
from scheduler.models import Session
from rest_framework import serializers


class EnrollmentNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnrollmentNote
        read_only_fields = (
            'id',
            'timestamp',
        )
        write_only_fields = (
            'enrollment',
        )
        fields = (
            'id',
            'enrollment',
            'timestamp',
            'title',
            'body',
            'important',
            'complete',
        )


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
    enrollment_id_list = serializers.SerializerMethodField()

    def get_enrollment_list(self, obj):
        return obj.enrollment_list

    def get_enrollment_id_list(self, obj):
        return obj.enrollment_id_list

    def create(self, validated_data):
        with transaction.atomic():
            # create course
            course = Course.objects.create(**validated_data)
            course.save()
            if course.start_date and course.end_date:
                current_date = arrow.get(course.start_date)
                end_date = arrow.get(course.end_date)
                while current_date <= end_date:
                    start_datetime = datetime.combine(
                        current_date.datetime,
                        course.start_time
                    )
                    end_datetime = datetime.combine(
                        current_date.datetime,
                        course.end_time
                    )
                    session = Session.objects.create(
                        course=course,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        is_confirmed=course.type == 'C'
                    )
                    session.save()
                    current_date.shift(weeks=+1)

            return course

    class Meta:
        model = Course

        fields = (
            'course_id',
            'subject',
            'type',
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
            'enrollment_id_list',
        )

        read_only_fields = (
            'enrollment_list',
            'enrollment_id_list',
        )


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory

        fields = ('id', 'name', 'description')


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment

        fields = (
            'id',
            'student',
            'course',
            'payment',
        )

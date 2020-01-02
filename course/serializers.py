from datetime import datetime
import pytz

import arrow
from django.db import transaction
from rest_framework import serializers

from course.models import EnrollmentNote, CourseNote, Course, CourseCategory, Enrollment
from payment.serializers import PaymentSerializer
from scheduler.models import Session


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

    @transaction.atomic
    def create(self, validated_data):
        # create course
        course = Course.objects.create(**validated_data)
        num_sessions = 0
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
                start_datetime = pytz.timezone(
                    'US/Pacific').localize(start_datetime)
                end_datetime = pytz.timezone(
                    'US/Pacific').localize(end_datetime)

                Session.objects.create(
                    course=course,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    is_confirmed=True
                )
                num_sessions += 1
                current_date = current_date.shift(weeks=+1)

        course.num_sessions = num_sessions
        course.save()
        return course

    @transaction.atomic
    def update(self, instance, validated_data):
        sessions = Session.objects.filter(course=instance)

        if "start_time" in validated_data or "end_time" in validated_data:
            for session in sessions:
                session.start_datetime = validated_data

            instance.update(**validated_data)
            instance.save()
        return instance

    class Meta:
        model = Course

        fields = (
            'id',
            'subject',
            'type',
            'academic_level',
            'description',
            'instructor',
            'hourly_tuition',
            'total_tuition',
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
    payment_list = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Enrollment

        fields = (
            'id',
            'student',
            'course',
            'payment_list',
        )

        read_only_fields = [
            'id',
        ]

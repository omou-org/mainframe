from datetime import datetime

import arrow
from django.db import transaction
from django.db.models import Q

from course.models import EnrollmentNote, CourseNote, Course, CourseCategory, Enrollment
from scheduler.models import Session
from rest_framework import serializers

from pricing.models import PriceRule

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
                    session = Session.objects.create(
                        course=course,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        is_confirmed=course.course_type == 'C'
                    )
                    session.save()
                    num_sessions += 1
                    current_date = current_date.shift(weeks=+1)

            if course.course_type == 'S':
                priceRule = PriceRule.objects.filter(
                    Q(category = course.course_category) &
                    Q(academic_level = course.academic_level) &
                    Q(course_type = 'S'))[0]
                course.hourly_tuition = priceRule.hourly_tuition

            course.total_tuition = course.hourly_tuition * num_sessions
            course.num_sessions = num_sessions
            course.save()
            return course

    class Meta:
        model = Course

        fields = (
            'id',
            'course_id',
            'num_sessions',
            'subject',
            'course_type',
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
    class Meta:
        model = Enrollment

        fields = (
            'id',
            'student',
            'course',
            'payment',
        )

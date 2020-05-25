from datetime import datetime, timezone
import calendar
import pytz

import arrow
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from course.models import EnrollmentNote, CourseNote, Course, CourseCategory, Enrollment
from payment.serializers import PaymentSerializer
from pricing.models import PriceRule
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
        course.num_sessions = 0

        if course.start_date and course.end_date:
            course.day_of_week = calendar.day_name[course.start_date.weekday()].lower()
            current_date = arrow.get(course.start_date)
            end_date = arrow.get(course.end_date)

            confirmed_end_date = end_date
            if course.course_type == 'small_group' or course.course_type == 'tutoring':
                end_date = end_date.shift(weeks=+30)

            while current_date <= end_date:
                start_datetime = datetime.combine(
                    current_date.date(),
                    course.start_time
                )
                end_datetime = datetime.combine(
                    current_date.date(),
                    course.end_time
                )
                start_datetime = pytz.timezone(
                    'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
                end_datetime = pytz.timezone(
                    'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)

                Session.objects.create(
                    course=course,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    instructor=course.instructor,
                    is_confirmed=course.is_confirmed and current_date <= confirmed_end_date,
                    title=course.title
                )
                course.num_sessions += 1
                current_date = current_date.shift(weeks=+1)

        if course.course_type == 'class' and course.num_sessions and course.session_length and course.total_tuition:
            course.hourly_tuition = course.total_tuition / (course.num_sessions * course.session_length)
        else:
            course.hourly_tuition = 0

        if course.course_type == 'small_group' or course.course_type == 'tutoring':
            priceRule = PriceRule.objects.filter(
                Q(category=course.course_category) &
                Q(academic_level=course.academic_level) &
                Q(course_type=course.course_type))[0]
            course.hourly_tuition = priceRule.hourly_tuition
            course.total_tuition = course.hourly_tuition * course.num_sessions
        
        course.save()
        return course

    @transaction.atomic
    def update(self, instance, validated_data):
        now = datetime.now()
        sessions = Session.objects.filter(
            course=instance,
            start_datetime__gte=now
        )

        for session in sessions:
            pacific_tz = pytz.timezone('America/Los_Angeles')
            utc_start_datetime = session.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=pacific_tz)
            utc_end_datetime = session.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=pacific_tz)
            start_datetime = datetime.combine(
                utc_start_datetime.date(),
                validated_data.get('start_time', instance.start_time)
            )
            end_datetime = datetime.combine(
                utc_end_datetime.date(),
                validated_data.get('end_time', instance.end_time)
            )
            session.start_datetime = pacific_tz.localize(start_datetime).astimezone(pytz.utc)
            session.end_datetime = pacific_tz.localize(end_datetime).astimezone(pytz.utc)
            session.save()

        if 'end_date' in validated_data or validated_data.get('is_confirmed', False):
            latest_session = sessions.latest('start_datetime')
            if len(sessions) == 0 and validated_data.get('is_confirmed', False):
                current_date = arrow.get(validated_data['start_date'])
            else:
                current_date = arrow.get(
                    latest_session.start_datetime.date()).shift(weeks=+1)
            end_date = arrow.get(validated_data['end_date'])
            while current_date <= end_date:
                start_datetime = datetime.combine(
                    current_date.date(),
                    validated_data.get('start_time', instance.start_time)
                )
                end_datetime = datetime.combine(
                    current_date.date(),
                    validated_data.get('end_time', instance.end_time)
                )
                start_datetime = pytz.timezone(
                    'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
                end_datetime = pytz.timezone(
                    'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)

                Session.objects.create(
                    course=instance,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    instructor=validated_data.get('instructor', instance.instructor),
                    is_confirmed=True
                )
                instance.num_sessions += 1
                current_date = current_date.shift(weeks=+1)

        instance.save()
        Course.objects.filter(id=instance.id).update(**validated_data)
        instance.refresh_from_db()
        return instance

    class Meta:
        model = Course

        fields = (
            'id',
            'course_id',
            'title',
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
            'is_confirmed',
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
            'enrollment_balance',
            'sessions_left',
            'last_paid_session_datetime',
        )

        read_only_fields = [
            'id',
            'enrollment_balance',
            'sessions_left',
            'last_paid_session_datetime',
        ]

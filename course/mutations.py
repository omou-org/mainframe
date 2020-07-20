import arrow
import calendar
import pytz
from datetime import datetime, timezone

import graphene
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from graphene import Boolean, DateTime, Decimal, Field, ID, Int, String, Time
from graphql import GraphQLError
from graphql_jwt.decorators import staff_member_required

from account.mutations import DayOfWeekEnum
from course.models import Course, CourseNote, CourseCategory, Enrollment, EnrollmentNote
from course.schema import (
    CourseType,
    CourseNoteType,
    CourseCategoryType,
    EnrollmentType,
    EnrollmentNoteType,
)
from scheduler.models import Session
from pricing.models import PriceRule


class CourseTypeEnum(graphene.Enum):
    TUTORING = 'tutoring'
    SMALL_GROUP = 'small_group'
    CLASS = 'class'


class AcademicLevelEnum(graphene.Enum):
    ELEMENTARY_LVL = 'elementary_lvl'
    MIDDLE_LVL = 'middle_lvl'
    HIGH_LVL = 'high_lvl'
    COLLEGE_LVL = 'college_lvl'


class CreateCourse(graphene.Mutation):
    class Arguments:
        course_id = ID(name='id')
        course_type = CourseTypeEnum()
        academic_level = AcademicLevelEnum()
        title = String()
        description = String()
        instructor_id = ID(name='instructor')
        hourly_tuition = Decimal()
        total_tuition = Decimal()
        course_category_id = ID(name='courseCategory')

        # Logistical information
        room = String()
        day_of_week = DayOfWeekEnum()
        start_date = DateTime()
        end_date = DateTime()
        start_time = Time()
        end_time = Time()
        max_capacity = Int()
        is_confirmed = Boolean()

    course = Field(CourseType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        # update course
        if validated_data.get('id'):
            course = Course.objects.get(id=validated_data.get('id'))
            now = datetime.now()
            sessions = Session.objects.filter(
                course=course,
                start_datetime__gte=now
            )

            for session in sessions:
                pacific_tz = pytz.timezone('America/Los_Angeles')
                utc_start_datetime = session.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=pacific_tz)
                utc_end_datetime = session.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=pacific_tz)
                start_datetime = datetime.combine(
                    utc_start_datetime.date(),
                    validated_data.get('start_time', course.start_time)
                )
                end_datetime = datetime.combine(
                    utc_end_datetime.date(),
                    validated_data.get('end_time', course.end_time)
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
                        validated_data.get('start_time', course.start_time)
                    )
                    end_datetime = datetime.combine(
                        current_date.date(),
                        validated_data.get('end_time', course.end_time)
                    )
                    start_datetime = pytz.timezone(
                        'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
                    end_datetime = pytz.timezone(
                        'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)

                    Session.objects.create(
                        course=course,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        instructor=validated_data.get('instructor', course.instructor),
                        is_confirmed=True
                    )
                    course.num_sessions += 1
                    current_date = current_date.shift(weeks=+1)

            course.save()
            Course.objects.filter(id=course.id).update(**validated_data)
            course.refresh_from_db()
            return CreateCourse(course=course, created=False)

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
            price_rule = PriceRule.objects.filter(
                Q(category=course.course_category) &
                Q(academic_level=course.academic_level) &
                Q(course_type=course.course_type))[0]
            course.hourly_tuition = price_rule.hourly_tuition
            course.total_tuition = course.hourly_tuition * course.num_sessions

        course.save()
        return CreateCourse(course=course, created=True)


class CreateCourseCategory(graphene.Mutation):
    class Arguments:
        category_id = ID(name='id')
        name = String()
        description = String()

    course_category = Field(CourseCategoryType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        course_category, created = CourseCategory.objects.update_or_create(
            id=validated_data.pop('category_id', None),
            defaults=validated_data
        )
        return CreateCourseCategory(course_category=course_category, created=created)


class CreateCourseNote(graphene.Mutation):
    class Arguments:
        note_id = ID(name='id')
        title = String()
        body = String()
        course_id = ID(name='course')
        important = Boolean()
        complete = Boolean()

    course_note = graphene.Field(CourseNoteType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        course_note, created = CourseNote.objects.update_or_create(
            id=validated_data.pop('note_id', None),
            defaults=validated_data
        )
        return CreateCourseNote(course_note=course_note, created=created)


class DeleteCourseNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(name='id')

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            note_obj = CourseNote.objects.get(id=validated_data.get('note_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. CourseNote does not exist.')
        note_obj.delete()
        return DeleteCourseNote(deleted=True)


class CreateEnrollment(graphene.Mutation):
    class Arguments:
        student_id = ID(name='student', required=True)
        course_id = ID(name='course', required=True)

    enrollment = graphene.Field(EnrollmentType)

    @staticmethod
    def mutate(root, info, **validated_data):
        enrollment = Enrollment.objects.create(**validated_data)
        return CreateEnrollment(enrollment=enrollment)


class CreateEnrollmentNote(graphene.Mutation):
    class Arguments:
        note_id = ID(name='id')
        title = String()
        body = String()
        enrollment_id = ID(name='enrollment')
        important = Boolean()
        complete = Boolean()

    enrollment_note = graphene.Field(EnrollmentNoteType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        enrollment_note, created = EnrollmentNote.objects.update_or_create(
            id=validated_data.pop('note_id', None),
            defaults=validated_data
        )
        return CreateEnrollmentNote(enrollment_note=enrollment_note, created=created)


class DeleteEnrollmentNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(name='id')

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            note_obj = EnrollmentNote.objects.get(id=validated_data.get('note_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. EnrollmentNote does not exist.')
        note_obj.delete()
        return DeleteEnrollmentNote(deleted=True)


class Mutation(graphene.ObjectType):
    create_course = CreateCourse.Field()
    create_course_category = CreateCourseCategory.Field()
    create_course_note = CreateCourseNote.Field()
    create_enrollment = CreateEnrollment.Field()
    create_enrollment_note = CreateEnrollmentNote.Field()

    delete_course_note = DeleteCourseNote.Field()
    delete_enrollment_note = DeleteEnrollmentNote.Field()

import arrow
import calendar
import graphene
import pytz
from datetime import datetime, timezone

from django.db.models import Q
from graphene import Boolean, DateTime, Decimal, Field, ID, Int, String, Time
from graphql_jwt.decorators import staff_member_required

from course.models import Course, CourseNote, CourseCategory, Enrollment, EnrollmentNote
from course.schema import CourseType, CourseNoteType, CourseCategoryType, EnrollmentType, EnrollmentNoteType
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


class DayOfWeekEnum(graphene.Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'


class CreateCourse(graphene.Mutation):
    class Arguments:
        course_type = CourseTypeEnum()
        academic_level = AcademicLevelEnum()
        title = String(required=True)
        description = String()
        instructor_id = ID(name='instructor')
        hourly_tuition = Decimal()
        total_tuition = Decimal()
        course_category_id = ID(name='course_category')

        # Logistical information
        room = String()
        day_of_week = DayOfWeekEnum()
        start_date = DateTime()
        end_date = DateTime()
        start_time = Time(required=True)
        end_time = Time(required=True)
        max_capacity = Int()
        is_confirmed = Boolean()

    course = Field(CourseType)

    @staticmethod
    def mutate(root, info, **validated_data):
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
        return CreateCourse(course=course)


class CreateCourseCategory(graphene.Mutation):
    class Arguments:
        name = String(required=True)
        description = String()

    course_category = Field(CourseCategoryType)

    @staticmethod
    def mutate(root, info, **validated_data):
        course_category = CourseCategory.objects.create(**validated_data)
        return CreateCourseCategory(course_category=course_category)


class CreateCourseNote(graphene.Mutation):
    class Arguments:
        title = String()
        body = String(required=True)
        course_id = ID(name='course', required=True)
        important = Boolean()
        complete = Boolean()

    course_note = graphene.Field(CourseNoteType)

    @staticmethod
    def mutate(root, info, **validated_data):
        course_note = CourseNote.objects.create(**validated_data)
        return CreateCourseNote(course_note=course_note)


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
        title = String()
        body = String(required=True)
        enrollment_id = ID(name='enrollment', required=True)
        important = Boolean()
        complete = Boolean()

    enrollment_note = graphene.Field(EnrollmentNoteType)

    @staticmethod
    def mutate(root, info, **validated_data):
        enrollment_note = EnrollmentNote.objects.create(**validated_data)
        return CreateEnrollmentNote(enrollment_note=enrollment_note)


class Mutation(graphene.ObjectType):
    create_course = CreateCourse.Field()
    create_course_category = CreateCourseCategory.Field()
    create_course_note = CreateCourseNote.Field()
    create_enrollment = CreateEnrollment.Field()
    create_enrollment_note = CreateEnrollmentNote.Field()

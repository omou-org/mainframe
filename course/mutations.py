import arrow
import calendar
import decimal
import pytz
from datetime import date, datetime, timedelta, timezone

import graphene
from graphene import Boolean, DateTime, Decimal, Field, ID, Int, List, String, Time
from graphql import GraphQLError
from graphql_jwt.decorators import staff_member_required

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from account.mutations import DayOfWeekEnum
from course.models import Course, CourseAvailability, CourseNote, CourseCategory, Enrollment, EnrollmentNote
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


class CourseAvailabilityInput(graphene.InputObjectType):
    day_of_week = DayOfWeekEnum()
    start_time = Time()
    end_time = Time()


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

        course_link = String()
        course_link_description = String()

        # Logistical information
        room = String()
        start_date = DateTime()
        end_date = DateTime()
        max_capacity = Int()
        is_confirmed = Boolean()
        availabilities = List(CourseAvailabilityInput)

    course = Field(CourseType)
    created = Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        # update course
        if validated_data.get('course_id'):
            course = Course.objects.get(id=validated_data.get('course_id'))
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
            if validated_data.get('course_link') or validated_data.get('course_link_description'):
                validated_data['course_link_updated_at'] = datetime.now()
            Course.objects.filter(id=course.id).update(**validated_data)
            course.refresh_from_db()

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Course).pk,
                object_id=course.id,
                object_repr=course.title,
                action_flag=CHANGE
            )
            return CreateCourse(course=course, created=False)

        # create course
        availabilities = validated_data.pop('availabilities')
        if not availabilities:
            raise GraphQLError('Failed course creation mutation. Availabilities does not exist.')
        if validated_data.get("hourly_tuition") and validated_data.get("total_tuition"):
            raise GraphQLError('Failed course creation mutation. Cannot specify both hourly_tuition and total_tuition')
        
        course = Course.objects.create(**validated_data)
        course.num_sessions = 0
        if validated_data.get('course_link') or validated_data.get('course_link_description'):
            course.course_link_updated_at = datetime.now()

        # create first week days and course availability models
        course_availabilities = []
        days_of_week = []
        start_times = []
        end_times = []
    
        start_date = arrow.get(course.start_date)
        week_start = start_date - timedelta(days=start_date.weekday())
        weekday_to_shift = {name.lower():i for i, name in enumerate(list(calendar.day_name))}

        for availability in availabilities:
            course_availabilities.append(
                CourseAvailability.objects.create(course=course, **availability)
            )
            days_of_week.append(
                week_start.shift(days=weekday_to_shift[availability.day_of_week])
            )
            start_times.append(availability.start_time)
            end_times.append(availability.end_time)
        
        # create sessions for each week till last date passes 
        if course.start_date and course.end_date:
            end_date = arrow.get(course.end_date)
            confirmed_end_date = end_date

            end_not_reached = True
            while end_not_reached:
                # for each week iterate over all availabilities
                for i in range(len(days_of_week)):
                    current_date = days_of_week[i]

                    # stop iterating once any current_date exceeds end_date
                    if current_date > end_date:
                        end_not_reached = False

                    if start_date <= current_date and current_date <= end_date:
                        start_datetime = datetime.combine(
                            current_date.date(),
                            start_times[i]
                        )
                        end_datetime = datetime.combine(
                            current_date.date(),
                            end_times[i]
                        )
                        start_datetime = pytz.timezone(
                            'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
                        end_datetime = pytz.timezone(
                            'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)

                        Session.objects.create(
                            course=course,
                            availability=course_availabilities[i],
                            start_datetime=start_datetime,
                            end_datetime=end_datetime,
                            instructor=course.instructor,
                            is_confirmed=course.is_confirmed and current_date <= confirmed_end_date,
                            title=course.title
                        )
                        course_availabilities[i].num_sessions += 1
                        course.num_sessions += 1
                    days_of_week[i] = current_date.shift(weeks=+1)
        
        # save updated availability num_sessions 
        for availability in course_availabilities:
            availability.save()

        if course.course_type == 'class' and course.num_sessions:
            # calculate total hours across all sessions
            total_hours = decimal.Decimal('0.0')
            for availability in course_availabilities:
                duration_sec = (datetime.combine(date.min, availability.end_time) - 
                                datetime.combine(date.min, availability.start_time)).seconds
                duration_hours = decimal.Decimal(duration_sec) / (60 * 60)
                total_hours += duration_hours * availability.num_sessions

            if course.total_tuition:
                course.hourly_tuition = course.total_tuition / total_hours
            elif course.hourly_tuition:
                course.total_tuition = course.hourly_tuition * total_hours
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
        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Course).pk,
            object_id=course.id,
            object_repr=course.title,
            action_flag=ADDITION
        )
        return CreateCourse(course=course, created=True)


class CreateCourseCategory(graphene.Mutation):
    class Arguments:
        category_id = ID(name='id')
        name = String()
        description = String()

    course_category = Field(CourseCategoryType)
    created = Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        course_category, created = CourseCategory.objects.update_or_create(
            id=validated_data.get('category_id', None),
            defaults=validated_data
        )
        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(CourseCategory).pk,
            object_id=course_category.id,
            object_repr=course_category.name,
            action_flag=CHANGE if 'category_id' in validated_data else ADDITION
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


class EnrollmentInput(graphene.InputObjectType):
    id = graphene.ID()
    student_id = graphene.ID(name='student')
    course_id = graphene.ID(name='course')


class CreateEnrollments(graphene.Mutation):
    class Arguments:
        enrollments = graphene.List(EnrollmentInput, required=True)

    enrollments = graphene.List(EnrollmentType)

    @staticmethod
    def mutate(root, info, **validated_data):
        objs = [Enrollment(**data) for data in validated_data['enrollments']]
        enrollments = Enrollment.objects.bulk_create(objs)
        return CreateEnrollments(
            enrollments=enrollments
        )


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

        

class DeleteEnrollment(graphene.Mutation):
    class Arguments:
        enrollment_id = graphene.ID(name='id')

    deleted = graphene.Boolean()
    parent = graphene.ID()
    parent_balance = graphene.Float()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            enrollment_obj = Enrollment.objects.get(id=validated_data.get('enrollment_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. Enrollment does not exist.')
        if enrollment_obj.student.primary_parent:
            parent = enrollment_obj.student.primary_parent
        else:
            parent = enrollment_obj.student.secondary_parent
        parent.balance += enrollment_obj.enrollment_balance
        parent.save()
        enrollment_obj.delete()
        return DeleteEnrollment(deleted=True, parent=parent.user.id, parent_balance=parent.balance)


class Mutation(graphene.ObjectType):
    create_course = CreateCourse.Field()
    create_course_category = CreateCourseCategory.Field()
    create_course_note = CreateCourseNote.Field()
    create_enrollment = CreateEnrollment.Field()    
    create_enrollments = CreateEnrollments.Field()
    create_enrollment_note = CreateEnrollmentNote.Field()

    delete_course_note = DeleteCourseNote.Field()
    delete_enrollment_note = DeleteEnrollmentNote.Field()
    delete_enrollment = DeleteEnrollment.Field()

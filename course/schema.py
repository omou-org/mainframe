import arrow

from graphene import Enum, Field, Int, List, ID, Decimal, DateTime, String
from graphene_django.types import ObjectType, DjangoObjectType
from graphql_jwt.decorators import login_required

from account.models import (
    Parent,
    Instructor
)

from course.models import (
    Course,
    CourseAvailability,
    CourseCategory,
    CourseNote,
    Enrollment,
    EnrollmentNote,
    Interest,
)
from scheduler.models import Session


class CourseAvailabilityType(DjangoObjectType):
    class Meta:
        model = CourseAvailability


class CourseType(DjangoObjectType):
    active_availability_list = List(CourseAvailabilityType, source='active_availability_list')
    availability_list = List(CourseAvailabilityType, source='availability_list')

    academic_level_pretty = String()
    class Meta:
        model = Course

    def resolve_academic_level_pretty(self, info):
        level_to_pretty = {
            "elementary_lvl": "elementary school",
            "middle_lvl": "middle school",
            "high_lvl": "high school",
            "college_lvl": "college"
        }
        academic_name = level_to_pretty.get(self.academic_level)
        return academic_name


class CourseCategoryType(DjangoObjectType):
    class Meta:
        model = CourseCategory


class CourseNoteType(DjangoObjectType):
    class Meta:
        model = CourseNote


class EnrollmentType(DjangoObjectType):
    enrollment_balance = Decimal(source='enrollment_balance')
    sessions_left = Int(source='sessions_left')
    last_paid_session_datetime = DateTime(source='last_paid_session_datetime')

    class Meta:
        model = Enrollment


class EnrollmentNoteType(DjangoObjectType):
    class Meta:
        model = EnrollmentNote


class InterestType(DjangoObjectType):
    class Meta:
        model = Interest


class LookbackTimeframe(Enum):
    YESTERDAY = 1
    LAST_WEEK = 2
    LAST_MONTH = 3
    ALL_TIME = 4


class PopularCategoryType(ObjectType):
    category = Field(CourseCategoryType)
    num_sessions = Int()


class Query(object):
    course = Field(CourseType, course_id=ID())
    course_availability = Field(CourseAvailabilityType, availability_id=ID())
    course_category = Field(CourseCategoryType, category_id=ID())
    course_note = Field(CourseNoteType, note_id=ID())
    enrollment = Field(EnrollmentType, enrollment_id=ID())
    enrollment_note = Field(EnrollmentNoteType, note_id=ID())
    interest = Field(InterestType, interest_id=ID())

    courses = List(CourseType, category_id=ID(), course_ids=List(ID), user_id=ID())
    course_availabilities = List(CourseAvailabilityType, course_id=ID(), availability_ids=List(ID))
    course_categories = List(CourseCategoryType)
    course_notes = List(CourseNoteType, course_id=ID(required=True))
    enrollments = List(EnrollmentType, student_id=ID(), course_id=ID(), student_ids=List(ID))
    enrollment_notes = List(EnrollmentNoteType, enrollment_id=ID(required=True))
    interests = List(InterestType, parent_id=ID(), course_id=ID())

    # custom methods
    num_recent_sessions = Int(timeframe=LookbackTimeframe(required=True))
    popular_categories = List(PopularCategoryType, timeframe=LookbackTimeframe(required=True))

    @login_required
    def resolve_course_availability(self, info, **kwargs):
        availability_id = kwargs.get('availability_id')

        if availability_id:
            return CourseAvailability.objects.get(id=availability_id)

        return None

    @login_required
    def resolve_course_availabilities(self, info, **kwargs):
        course_id = kwargs.get('course_id')
        availability_ids = kwargs.get('availability_ids')

        if course_id:
            return CourseAvailability.objects.filter(course_id=course_id)

        if availability_ids:
             return CourseAvailability.objects.filter(id__in=availability_ids)

        return None

    @login_required
    def resolve_course(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        if course_id:
            return Course.objects.get(id=course_id)

        return None

    @login_required
    def resolve_course_category(self, info, **kwargs):
        category_id = kwargs.get('category_id')

        if category_id:
            return CourseCategory.objects.get(id=category_id)

        return None

    @login_required
    def resolve_course_note(self, info, **kwargs):
        note_id = kwargs.get('course_note')

        if note_id:
            return CourseNote.objects.get(id=note_id)

        return None

    @login_required
    def resolve_enrollment(self, info, **kwargs):
        enrollment_id = kwargs.get('enrollment_id')

        if enrollment_id:
            return Enrollment.objects.get(id=enrollment_id)

        return None

    @login_required
    def resolve_enrollment_note(self, info, **kwargs):
        note_id = kwargs.get('note_id')

        if note_id:
            return Enrollment.objects.get(id=note_id)

        return None

    @login_required
    def resolve_interest(self, info, **kwargs):
        interest_id = kwargs.get('interest_id')

        if interest_id:
            return Interest.objects.get(id=interest_id)
        
        return None

    @login_required
    def resolve_courses(self, info, **kwargs):
        category_id = kwargs.get('category_id')
        course_ids = kwargs.get('course_ids')
        user_id = kwargs.get('user_id')

        if category_id:
            return Course.objects.filter(course_category=category_id)
        if course_ids:
            course_ids = [course_id for course_id in course_ids if Course.objects.filter(id=course_id).exists()]
            return Course.objects.filter(id__in = course_ids) 
        if user_id:
            if Instructor.objects.filter(user_id=user_id).exists():
                return Course.objects.filter(instructor_id=user_id)
            if Parent.objects.filter(user_id=user_id).exists():
                parent = Parent.objects.get(user_id=user_id)
                student_course_ids = set()
                for student_id in parent.student_list:
                    for enrollment in Enrollment.objects.filter(student=student_id):
                        student_course_ids.add(enrollment.course.id)
                return Course.objects.filter(id__in = student_course_ids) 
        return Course.objects.all()

    @login_required
    def resolve_course_categories(self, info, **kwargs):
        return CourseCategory.objects.all()

    @login_required
    def resolve_course_notes(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        return CourseNote.objects.filter(course__id=course_id)

    @login_required
    def resolve_enrollments(self, info, **kwargs):
        student_id = kwargs.get('student_id')
        course_id = kwargs.get('course_id')
        student_ids = kwargs.get('student_ids')
        enrollment_list = []

        queryset = Enrollment.objects

        if student_id:
            queryset = queryset.filter(student=student_id)
        if course_id:
            queryset = queryset.filter(course=course_id)
        if student_ids:
            enrollment_list = Enrollment.objects.filter(student_id__in=student_ids)
        return enrollment_list or queryset.all()

    @login_required
    def resolve_enrollment_notes(self, info, **kwargs):
        enrollment_id = kwargs.get('enrollment_id')

        return EnrollmentNote.objects.filter(enrollment_id=enrollment_id)

    def resolve_num_recent_sessions(self, info, timeframe, **kwargs):
        now = arrow.now()

        if timeframe == LookbackTimeframe.YESTERDAY:
            return Session.objects.filter(
                start_datetime__gte=now.shift(days=-1).datetime,
                start_datetime__lte=now.datetime
            ).count()
        elif timeframe == LookbackTimeframe.LAST_WEEK:
            return Session.objects.filter(
                start_datetime__gte=now.shift(weeks=-1).datetime,
                start_datetime__lte=now.datetime
            ).count()
        elif timeframe == LookbackTimeframe.LAST_MONTH:
            return Session.objects.filter(
                start_datetime__gte=now.shift(months=-1).datetime,
                start_datetime__lte=now.datetime
            ).count()
        elif timeframe == LookbackTimeframe.ALL_TIME:
            return Session.objects.filter(
                start_datetime__lte=now.datetime
            ).count()

        return None

    def resolve_popular_categories(self, info, timeframe, **kwargs):
        category_counts = []
        categories = CourseCategory.objects.all()

        for category in categories:
            courses = category.course_set.all()
            num_sessions = 0
            now = arrow.now()

            for course in courses:
                if timeframe == LookbackTimeframe.YESTERDAY:
                    num_sessions += course.session_set.filter(
                        start_datetime__gte=now.shift(days=-1).datetime,
                        start_datetime__lte=now.datetime
                    ).count()
                elif timeframe == LookbackTimeframe.LAST_WEEK:
                    num_sessions += course.session_set.filter(
                        start_datetime__gte=now.shift(weeks=-1).datetime,
                        start_datetime__lte=now.datetime
                    ).count()
                elif timeframe == LookbackTimeframe.LAST_MONTH:
                    num_sessions += course.session_set.filter(
                        start_datetime__gte=now.shift(months=-1).datetime,
                        start_datetime__lte=now.datetime
                    ).count()
                elif timeframe == LookbackTimeframe.ALL_TIME:
                    num_sessions += course.session_set.filter(
                        start_datetime__lte=now.datetime
                    ).count()

            category_counts.append({'category': category, 'num_sessions': num_sessions})

        top_5_categories = sorted(
            category_counts,
            key=lambda item: item['num_sessions'],
            reverse=True
        )[:5]

        return top_5_categories
    
    @login_required
    def resolve_interests(self, info, **kwargs):
        parent_id = kwargs.get('parent_id')
        course_id = kwargs.get('course_id')

        if parent_id:
            return Interest.objects.filter(parent__user__id=parent_id)
        
        if course_id:
            return Interest.objects.filter(course=course_id)
        
        return None

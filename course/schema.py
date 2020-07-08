import arrow

from graphene import Enum, Field, Int, List, ID, Decimal, DateTime, String
from graphene_django.types import ObjectType, DjangoObjectType
from graphql_jwt.decorators import login_required

from course.models import (
    Course,
    CourseCategory,
    CourseNote,
    Enrollment,
    EnrollmentNote,
)
from scheduler.models import Session


class CourseType(DjangoObjectType):
    class Meta:
        model = Course


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
    course_category = Field(CourseCategoryType, category_id=ID())
    course_note = Field(CourseNoteType, note_id=ID())
    enrollment = Field(EnrollmentType, enrollment_id=ID())
    enrollment_note = Field(EnrollmentNoteType, note_id=ID())

    courses = List(CourseType, category_id=ID(), course_ids=List(ID))
    course_categories = List(CourseCategoryType)
    course_notes = List(CourseNoteType, course_id=ID(required=True))
    enrollments = List(EnrollmentType, student_id=ID(), course_id=ID())
    enrollment_notes = List(EnrollmentNoteType, enrollment_id=ID(required=True))

    # custom methods
    num_recent_sessions = Int(timeframe=LookbackTimeframe(required=True))
    popular_categories = List(PopularCategoryType, timeframe=LookbackTimeframe(required=True))

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
    def resolve_enrollment_note(self, info, **kwargs):
        note_id = kwargs.get('note_id')

        if note_id:
            return Enrollment.objects.get(id=note_id)

        return None

    @login_required
    def resolve_courses(self, info, **kwargs):
        category_id = kwargs.get('category_id')
        course_ids = kwargs.get('course_ids')
        course_list = []

        if category_id:
            return Course.objects.filter(course_category=category_id)
        for course_id in course_ids:
            if Course.objects.filter(id=course_id).exists():
                course_list.append(Course.objects.get(id=course_id))

        return course_list or Course.objects.all()

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

        queryset = Enrollment.objects

        if student_id:
            queryset = queryset.filter(student=student_id)
        if course_id:
            queryset = queryset.filter(course=course_id)
        return queryset.all()

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



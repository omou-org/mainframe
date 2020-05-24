from graphene import Field, Int, List, String
from graphene_django.types import DjangoObjectType

from course.models import (
    Course,
    CourseCategory,
    CourseNote,
    Enrollment,
    EnrollmentNote,
)


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
    class Meta:
        model = Enrollment


class EnrollmentNoteType(DjangoObjectType):
    class Meta:
        model = EnrollmentNote


class Query(object):
    course = Field(CourseType, course_id=Int())
    course_category = Field(CourseCategoryType, category_id=Int())
    course_note = Field(CourseNoteType, note_id=Int())
    enrollment = Field(EnrollmentType, enrollment_id=Int())
    enrollment_note = Field(EnrollmentNoteType, note_id=Int())

    courses = List(CourseType, category_id=Int())
    course_categories = List(CourseCategoryType)
    course_notes = List(CourseNoteType, course_id=Int(required=True))
    enrollments = List(EnrollmentType, student_id=Int(), course_id=Int())
    enrollment_notes = List(EnrollmentNoteType, enrollment_id=Int(required=True))

    def resolve_course(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        if course_id:
            return Course.objects.get(id=course_id)

        return None

    def resolve_course_category(self, info, **kwargs):
        category_id = kwargs.get('category_id')

        if category_id:
            return CourseCategory.objects.get(id=category_id)

        return None

    def resolve_course_note(self, info, **kwargs):
        note_id = kwargs.get('course_note')

        if note_id:
            return CourseNote.objects.get(id=note_id)

        return None

    def resolve_enrollment_note(self, info, **kwargs):
        note_id = kwargs.get('note_id')

        if note_id:
            return Enrollment.objects.get(id=note_id)

        return None

    def resolve_courses(self, info, **kwargs):
        category_id = kwargs.get('category_id')

        if category_id:
            return Course.objects.filter(course_category=category_id)
        return Course.objects.all()

    def resolve_course_categories(self, info, **kwargs):
        return CourseCategory.objects.all()

    def resolve_course_notes(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        return CourseNote.objects.filter(course__id=course_id)

    def resolve_enrollments(self, info, **kwargs):
        student_id = kwargs.get('student_id')
        course_id = kwargs.get('course_id')

        queryset = Enrollment.objects

        if student_id:
            queryset = queryset.filter(student=student_id)
        if course_id:
            queryset = queryset.filter(course=course_id)
        return queryset.all()

    def resolve_enrollment_notes(self, info, **kwargs):
        enrollment_id = kwargs.get('enrollment_id')

        return EnrollmentNote.objects.filter(enrollment_id=enrollment_id)

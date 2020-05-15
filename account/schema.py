from graphene import Field, Int, List, String
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model

from account.models import (
    Note,
    School,
    Student,
    Parent,
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
    Admin,
)

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User


class NoteType(DjangoObjectType):
    class Meta:
        model = Note


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class StudentType(DjangoObjectType):
    class Meta:
        model = Student


class ParentType(DjangoObjectType):
    class Meta:
        model = Parent


class InstructorType(DjangoObjectType):
    class Meta:
        model = Instructor


class InstructorAvailabilityType(DjangoObjectType):
    class Meta:
        model = InstructorAvailability


class InstructorOutOfOfficeType(DjangoObjectType):
    class Meta:
        model = InstructorOutOfOffice


class AdminType(DjangoObjectType):
    class Meta:
        model = Admin


class Query(object):
    note = Field(NoteType, id=Int())
    student = Field(StudentType, user=Int(), email=String())
    school = Field(SchoolType, id=Int(), name=String())
    parent = Field(ParentType, user=Int(), email=String())
    instructor = Field(InstructorType, user=Int(), email=String())
    instructor_out_of_office = List(
        InstructorOutOfOfficeType,
        instructor_id=Int()
    )
    instructor_availability = List(
        InstructorAvailabilityType,
        instructor_id=Int()
    )
    admin = Field(AdminType, user=Int(), email=String())

    all_notes = List(NoteType, user=Int())
    all_schools = List(SchoolType, district=String())
    all_students = List(StudentType, grade=Int())
    all_parents = List(ParentType)
    all_instructors = List(InstructorType, subject=String())
    all_admin = List(AdminType, admin_type=String())

    def resolve_note(self, info, **kwargs):
        note_id = kwargs.get('id')

        if id:
            return Note.objects.get(id=id)

        return None

    def resolve_student(self, info, **kwargs):
        user = kwargs.get('user')
        email = kwargs.get('email')

        if user:
            return Student.objects.get(user=user)

        if email:
            return Student.objects.get(user__email=email)

        return None

    def resolve_school(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')

        if id:
            return School.objects.get(id=id)

        if name:
            return School.objects.get(name=name)

        return None

    def resolve_parent(self, info, **kwargs):
        user = kwargs.get('user')
        email = kwargs.get('email')

        if user:
            return Parent.objects.get(id=id)

        if email:
            return Parent.objects.get(user__email=email)

        return None


    def resolve_instructor(self, info, **kwargs):
        user = kwargs.get('user')
        email = kwargs.get('email')

        if user:
            return Instructor.objects.get(id=id)

        if email:
            return Instructor.objects.get(user__email=email)

        return None

    def resolve_instructor_out_of_office(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')

        if instructor_id:
            return InstructorOutOfOffice.objects.filter(
                instructor=instructor_id
            )

        return None

    def resolve_instructor_availability(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')

        if instructor_id:
            return InstructorAvailability.objects.filter(
                instructor=instructor_id
            )

        return None

    def resolve_admin(self, info, **kwargs):
        user = kwargs.get('user')
        email = kwargs.get('email')

        if user:
            return Admin.objects.get(id=id)

        if email:
            return Admin.objects.get(user__email=email)

        return None

    def resolve_all_notes(self, info, **kwargs):
        user = kwargs


    def resolve_all_students(self, info, **kwargs):
        grade = kwargs.get('grade')

        if grade:
            return Student.objects.filter(grade=grade)
        return Student.objects.all()

    def resolve_all_schools(self, info, **kwargs):
        district = kwargs.get('district')
        queryset = School.objects

        if district:
            queryset = queryset.filter(district=district)

        return queryset.all()

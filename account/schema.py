
from graphene import Field, ID, Int, List, String, Union
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


class UserInfoType(Union):
    class Meta:
        types = (StudentType, ParentType, InstructorType, AdminType)


class Query(object):
    note = Field(NoteType, note_id=ID())
    student = Field(StudentType, user_id=ID(), email=String())
    school = Field(SchoolType, school_id=ID(), name=String())
    parent = Field(ParentType, user_id=ID(), email=String())
    instructor = Field(InstructorType, user_id=ID(), email=String())
    admin = Field(AdminType, user_id=ID(), email=String())
    user_info = Field(UserInfoType, user_id=ID())

    notes = List(NoteType, user_id=ID(required=True))
    students = List(StudentType, grade=ID())
    schools = List(SchoolType, district=String())
    parents = List(ParentType)
    instructors = List(InstructorType, subject=String())
    admins = List(AdminType, admin_type=String())

    instructor_ooo = List(
        InstructorOutOfOfficeType,
        instructor_id=ID(required=True)
    )
    instructor_availability = List(
        InstructorAvailabilityType,
        instructor_id=ID(required=True)
    )

    def resolve_note(self, info, **kwargs):
        note_id = kwargs.get('note_id')

        if note_id:
            return Note.objects.get(id=note_id)

        return None

    def resolve_student(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Student.objects.get(user=user_id)

        if email:
            return Student.objects.get(user__email=email)

        return None

    def resolve_school(self, info, **kwargs):
        school_id = kwargs.get('school_id')
        name = kwargs.get('name')

        if school_id:
            return School.objects.get(id=school_id)

        if name:
            return School.objects.get(name=name)

        return None

    def resolve_parent(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Parent.objects.get(user=user_id)

        if email:
            return Parent.objects.get(user__email=email)

        return None

    def resolve_instructor(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Instructor.objects.get(user=user_id)

        if email:
            return Instructor.objects.get(user__email=email)

        return None

    def resolve_admin(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Admin.objects.get(user=user_id)

        if email:
            return Admin.objects.get(user__email=email)

        return None

    def resolve_user_info(self, info, **kwargs):
        user_id = kwargs.get('user_id')

        return None

    def resolve_notes(self, info, **kwargs):
        user_id = kwargs.get('user_id')

        return Note.objects.filter(user=user_id)

    def resolve_students(self, info, **kwargs):
        grade = kwargs.get('grade')

        if grade:
            return Student.objects.filter(grade=grade)
        return Student.objects.all()

    def resolve_schools(self, info, **kwargs):
        district = kwargs.get('district')
        queryset = School.objects

        if district:
            queryset = queryset.filter(district=district)

        return queryset.all()

    def resolve_admins(self, info, **kwargs):
        admin_type = kwargs.get('admin_type')

        if admin_type:
            return Admin.objects.filter(admin_type=admin_type)
        return Admin.objects.all()

    def resolve_parents(self, info, **kwargs):
        return Parent.objects.all()

    def resolve_instructors(self, info, **kwargs):
        return Instructor.objects.all()

    def resolve_instructor_out_of_office(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')

        return InstructorOutOfOffice.objects.filter(instructor=instructor_id)

    def resolve_instructor_availability(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')

        return InstructorAvailability.objects.filter(instructor=instructor_id)

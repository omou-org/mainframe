import jwt
from datetime import datetime, date
from graphene import Field, ID, List, String, Boolean, Union, DateTime, ObjectType
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model

from account.models import (
    AccountNote,
    School,
    Student,
    StudentSchoolInfo,
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


class UserTypeAuth(ObjectType):
    user_type = String()
    google_auth_enabled = Boolean()


class AccountNoteType(DjangoObjectType):
    class Meta:
        model = AccountNote


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class StudentType(DjangoObjectType):
    class Meta:
        model = Student


class StudentSchoolInfoType(DjangoObjectType):
    class Meta:
        model = StudentSchoolInfo


class ParentType(DjangoObjectType):
    student_id_list = List(ID, source='student_id_list')
    student_list = List(StudentType, source='student_list')

    class Meta:
        model = Parent


class InstructorType(DjangoObjectType):
    class Meta:
        model = Instructor


class InstructorAvailabilityType(DjangoObjectType):
    start_datetime = DateTime()
    end_datetime = DateTime()
    class Meta:
        model = InstructorAvailability
    
    def resolve_start_datetime(self, info):
        return datetime.combine(date.today(), self.start_time)
    
    def resolve_end_datetime(self, info):
        return datetime.combine(date.today(), self.end_time)


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
    account_note = Field(AccountNoteType, note_id=ID())
    student = Field(StudentType, user_id=ID(), email=String())
    school = Field(SchoolType, school_id=ID(), name=String())
    parent = Field(ParentType, user_id=ID(), email=String())
    instructor = Field(InstructorType, user_id=ID(), email=String())
    admin = Field(AdminType, user_id=ID(), email=String())
    user_info = Field(UserInfoType, user_id=ID(), user_name=String())
    user_type = Field(UserTypeAuth, user_id=ID(), user_name=String(), admin_types=Boolean())
    email_from_token = Field(String, token=String())

    account_notes = List(AccountNoteType, user_id=ID(required=True))
    students = List(StudentType, grade=ID())
    schools = List(SchoolType, district=String())
    parents = List(ParentType)
    instructors = List(InstructorType, subject=String())
    admins = List(AdminType, admin_type=String())
    user_infos = List(UserInfoType, user_ids=List(ID))

    instructor_ooo = List(
        InstructorOutOfOfficeType,
        instructor_id=ID(required=True)
    )
    instructor_availability = List(
        InstructorAvailabilityType,
        instructor_id=ID(required=True)
    )

    @login_required
    def resolve_account_note(self, info, **kwargs):
        note_id = kwargs.get('note_id')

        if note_id:
            return AccountNote.objects.get(id=note_id)

        return None

    @login_required
    def resolve_student(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Student.objects.get(user=user_id)

        if email:
            return Student.objects.get(user__email=email)

        return None

    @login_required
    def resolve_school(self, info, **kwargs):
        school_id = kwargs.get('school_id')
        name = kwargs.get('name')

        if school_id:
            return School.objects.get(id=school_id)

        if name:
            return School.objects.get(name=name)

        return None

    @login_required
    def resolve_parent(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Parent.objects.get(user=user_id)

        if email:
            return Parent.objects.get(user__email=email)

        return None

    @login_required
    def resolve_instructor(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Instructor.objects.get(user=user_id)

        if email:
            return Instructor.objects.get(user__email=email)

        return None

    @login_required
    def resolve_admin(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        email = kwargs.get('email')

        if user_id:
            return Admin.objects.get(user=user_id)

        if email:
            return Admin.objects.get(user__email=email)

        return None

    def resolve_user_type(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        user_name = kwargs.get('user_name')
        admin_types = kwargs.get('admin_types')

        if user_name:
            if Student.objects.filter(user__email=user_name).exists():
                return UserTypeAuth(user_type="STUDENT", google_auth_enabled=False)
            if Instructor.objects.filter(user__email=user_name).exists():
                return UserTypeAuth(user_type="INSTRUCTOR", google_auth_enabled=False)
            if Parent.objects.filter(user__email=user_name).exists():
                return UserTypeAuth(user_type="PARENT", google_auth_enabled=False)
            if Admin.objects.filter(user__email=user_name).exists():
                admin = Admin.objects.get(user__email=user_name)
                if admin_types:
                    return Admin.objects.get(user__email=user_name).admin_type.upper()
                return UserTypeAuth(user_type="ADMIN", google_auth_enabled=admin.google_auth_enabled)
        
        if user_id:
            if Student.objects.filter(user=user_id).exists():
                return UserTypeAuth(user_type="STUDENT", google_auth_enabled=False)
            if Instructor.objects.filter(user=user_id).exists():
                return UserTypeAuth(user_type="INSTRUCTOR", google_auth_enabled=False)
            if Parent.objects.filter(user=user_id).exists():
                return UserTypeAuth(user_type="PARENT", google_auth_enabled=False)
            if Admin.objects.filter(user=user_id).exists():
                admin = Admin.objects.get(user__email=user_name)
                if admin_types:
                    return UserTypeAuth(user_type=admin.admin_type.upper(), google_auth_enabled=admin.google_auth_enabled)
                return UserTypeAuth(user_type="ADMIN", google_auth_enabled=admin.google_auth_enabled)

        return None

    @login_required
    def resolve_user_info(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        user_name = kwargs.get('user_name')

        if user_name:
            if Student.objects.filter(user__email=user_name).exists():
                return Student.objects.get(user__email=user_name)
            if Instructor.objects.filter(user__email=user_name).exists():
                return Instructor.objects.get(user__email=user_name)
            if Parent.objects.filter(user__email=user_name).exists():
                return Parent.objects.get(user__email=user_name)
            if Admin.objects.filter(user__email=user_name).exists():
                return Admin.objects.get(user__email=user_name)

        if user_id:
            if Student.objects.filter(user=user_id).exists():
                return Student.objects.get(user=user_id)
            if Instructor.objects.filter(user=user_id).exists():
                return Instructor.objects.get(user=user_id)
            if Parent.objects.filter(user=user_id).exists():
                return Parent.objects.get(user=user_id)
            if Admin.objects.filter(user=user_id).exists():
                return Admin.objects.get(user=user_id)

        return None

    @login_required
    def resolve_account_notes(self, info, **kwargs):
        user_id = kwargs.get('user_id')

        return AccountNote.objects.filter(user=user_id)

    def resolve_students(self, info, **kwargs):
        grade = kwargs.get('grade')

        if grade:
            return Student.objects.filter(grade=grade)
        return Student.objects.all()

    @login_required
    def resolve_schools(self, info, **kwargs):
        district = kwargs.get('district')
        queryset = School.objects

        if district:
            queryset = queryset.filter(district=district)

        return queryset.all()

    @login_required
    def resolve_admins(self, info, **kwargs):
        admin_type = kwargs.get('admin_type')

        if admin_type:
            return Admin.objects.filter(admin_type=admin_type)
        return Admin.objects.all()

    @login_required
    def resolve_parents(self, info, **kwargs):
        return Parent.objects.all()

    @login_required
    def resolve_instructors(self, info, **kwargs):
        return Instructor.objects.all()

    @login_required
    def resolve_instructor_ooo(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')

        return InstructorOutOfOffice.objects.filter(instructor=instructor_id)

    @login_required
    def resolve_instructor_availability(self, info, **kwargs):
        instructor_id = kwargs.get('instructor_id')
        return InstructorAvailability.objects.filter(instructor=instructor_id)

    def resolve_user_infos(self, info, user_ids):
        user_list = []

        for user_id in user_ids:
            if Student.objects.filter(user=user_id).exists():
                user_list.append(Student.objects.get(user=user_id))
            if Instructor.objects.filter(user=user_id).exists():
                user_list.append(Instructor.objects.get(user=user_id))
            if Parent.objects.filter(user=user_id).exists():
                user_list.append(Parent.objects.get(user=user_id))
            if Admin.objects.filter(user=user_id).exists():
                user_list.append(Admin.objects.get(user=user_id))

        return user_list

    def resolve_email_from_token(self, info, token):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["email"]

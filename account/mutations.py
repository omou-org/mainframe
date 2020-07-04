import graphene
import jwt
import uuid

from account.models import (
    Note,
    Admin,
    Student,
    School,
    Parent,
    Instructor,
)
from account.schema import (
    NoteType,
    AdminType,
    InstructorType,
    ParentType,
    SchoolType,
    StudentType,
)
from comms.models import Email
from comms.templates import RESET_PASSWORD_TEMPLATE

from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings
from graphql_jwt.decorators import login_required, staff_member_required
from rest_framework.authtoken.models import Token


class GenderEnum(graphene.Enum):
    MALE = 'male'
    FEMALE = 'female'
    UNSPECIFIED = 'unspecified'


class AdminTypeEnum(graphene.Enum):
    OWNER = 'owner'
    RECEPTIONIST = 'receptionist'
    ASSISTANT = 'assistant'


class CreateSchool(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        zipcode = graphene.String()
        district = graphene.String()

    school = graphene.Field(SchoolType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, name, zipcode, district):
        school = School.objects.create(name=name, zipcode=zipcode, district=district)
        return CreateSchool(school=school)


class UserInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String()
    password = graphene.String()


class CreateStudent(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = GenderEnum()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

        # Student fields
        grade = graphene.Int()
        school = graphene.Int()
        primary_parent = graphene.ID()
        secondary_parent = graphene.ID()

    student = graphene.Field(StudentType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # create user and token
            user_object = User.objects.create_user(
                username=uuid.uuid4(),
                password="password",
                first_name=user['first_name'],
                last_name=user['last_name'],
            )
            Token.objects.get_or_create(user=user_object)

            # create account
            student = Student.objects.create(
                user=user_object,
                account_type='student',
                **validated_data
            )
            return CreateStudent(student=student)


class CreateParent(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = GenderEnum()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

        # Parent fields
        relationship = graphene.String()
        secondary_phone_number = graphene.String()

    parent = graphene.Field(ParentType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # create user and token
            user_object = User.objects.create_user(
                username=user.get("email", uuid.uuid4()),
                email=user.get("email", None),
                first_name=user['first_name'],
                last_name=user['last_name'],
                password=user['password'],
            )
            Token.objects.get_or_create(user=user_object)

            # create account
            parent = Parent.objects.create(
                user=user_object,
                account_type='parent',
                **validated_data
            )
            return CreateParent(parent=parent)


class CourseCategoryInput(graphene.InputObjectType):
    id = graphene.Int()


class CreateInstructor(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = GenderEnum()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

        # Instructor fields
        biography = graphene.String()
        experience = graphene.String()
        language = graphene.String()
        subjects = graphene.List(graphene.ID)

    instructor = graphene.Field(InstructorType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # create user and token
            user_object = User.objects.create_user(
                username=user.get("email", uuid.uuid4()),
                email=user.get("email", None),
                first_name=user['first_name'],
                last_name=user['last_name'],
                password=user['password'],
            )
            Token.objects.get_or_create(user=user_object)
            subjects = validated_data.pop('subjects')

            # create account
            instructor = Instructor.objects.create(
                user=user_object,
                account_type='instructor',
                **validated_data,
            )
            instructor.subjects.set(subjects)
            instructor.save()
            return CreateInstructor(instructor=instructor)


class CreateAdmin(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = GenderEnum()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

        # Admin fields
        admin_type = AdminTypeEnum(required=True)

    admin = graphene.Field(AdminType)

    @staticmethod
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # create user and token
            user_object = User.objects.create_user(
                email=user['email'],
                username=user['email'],
                password=user['password'],
                first_name=user['first_name'],
                last_name=user['last_name'],
            )
            if validated_data['admin_type'] == Admin.OWNER_TYPE:
                user_object.is_staff = True
                user_object.save()
            Token.objects.get_or_create(user=user_object)

            # create account
            admin = Admin.objects.create(
                user=user_object,
                account_type='admin',
                **validated_data
            )
            return CreateAdmin(admin=admin)


class CreateNote(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        body = graphene.String()
        important = graphene.Boolean()
        complete = graphene.Boolean()

    note = graphene.Field(NoteType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        note = Note.objects.create(**validated_data)
        return CreateNote(note=note)


class RequestPasswordReset(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    status = graphene.String()
    error_message = graphene.String()

    @staticmethod
    def mutate(root, info, email):
        try:
            user = User.objects.get(email=email)
        except Exception:
            return RequestPasswordReset(status="failed", error_message="No such user exists.")

        token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

        email = Email(
            template_id=RESET_PASSWORD_TEMPLATE,
            recipient=email,
            data={"username": user.first_name, "token": token}
        )
        email.save()

        return RequestPasswordReset(status=email.status, error_message=email.response_body)


class ResetPassword(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        new_password = graphene.String(required=True)

    status = graphene.String()

    @staticmethod
    def mutate(root, info, token, new_password):
        try:
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["email"]
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
        except Exception:
            return ResetPassword(status="failed")

        return ResetPassword(status="success")


class Mutation(graphene.ObjectType):
    create_school = CreateSchool.Field()
    create_student = CreateStudent.Field()
    create_parent = CreateParent.Field()
    create_instructor = CreateInstructor.Field()
    create_admin = CreateAdmin.Field()
    create_note = CreateNote.Field()

    # Auth endpoints
    request_password_reset = RequestPasswordReset.Field()
    reset_password = ResetPassword.Field()

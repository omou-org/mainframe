import graphene
import pytz
import uuid

from account.models import (
    Note,
    Admin,
    Student,
    School,
    Parent,
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from account.schema import SchoolType, StudentType, UserType
from account.serializers import (
    StudentSerializer,
    AdminSerializer,
    ParentSerializer,
    InstructorSerializer
)

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from graphene_django.rest_framework.mutation import SerializerMutation


class CreateSchool(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        zipcode = graphene.String()
        district = graphene.String()

    school = graphene.Field(SchoolType)

    def mutate(self, info, name, zipcode, district):
        school = School.objects.create(name=name, zipcode=zipcode, district=district)
        return CreateSchool(school=school)


class UserInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String()


class CreateStudent(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = graphene.String()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

        # Student fields
        grade = graphene.Int()
        school = graphene.Int()
        primary_parent = graphene.Int()
        secondary_parent = graphene.Int()

    student = graphene.Field(StudentType)

    @staticmethod
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


class CreateAdmin(SerializerMutation):
    class Meta:
        serializer_class = AdminSerializer
        convert_choices_to_enum = False


class CreateParent(SerializerMutation):
    class Meta:
        serializer_class = ParentSerializer
        convert_choices_to_enum = False


class CreateInstructor(SerializerMutation):
    class Meta:
        serializer_class = InstructorSerializer
        convert_choices_to_enum = False


class Mutation(graphene.ObjectType):
    create_school = CreateSchool.Field()
    create_student = CreateStudent.Field()
    create_admin = CreateAdmin.Field()
    create_parent = CreateParent.Field()
    create_instructor = CreateInstructor.Field()

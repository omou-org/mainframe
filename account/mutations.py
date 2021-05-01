import jwt
import pytz
import uuid

import graphene
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required
from rest_framework.authtoken.models import Token

from account.models import (
    AccountNote,
    Admin,
    Student,
    School,
    Parent,
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from account.schema import (
    AccountNoteType,
    AdminType,
    ParentType,
    SchoolType,
    StudentType,
    InstructorType,
    InstructorAvailabilityType,
    InstructorOutOfOfficeType,
)
from comms.models import Email, ParentNotificationSettings
from comms.templates import (
    RESET_PASSWORD_TEMPLATE,
    INVITE_INSTRUCTOR_TEMPLATE,
    INVITE_STUDENT_TEMPLATE,
    WELCOME_PARENT_TEMPLATE,
)


class GenderEnum(graphene.Enum):
    MALE = 'male'
    FEMALE = 'female'
    UNSPECIFIED = 'unspecified'


class AdminTypeEnum(graphene.Enum):
    OWNER = 'owner'
    RECEPTIONIST = 'receptionist'
    ASSISTANT = 'assistant'


class DayOfWeekEnum(graphene.Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'


class RelationshipEnum(graphene.Enum):
    MOTHER = 'mother'
    FATHER = 'father'
    GUARDIAN = 'guardian'
    OTHER = 'other'


class CreateSchool(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        zipcode = graphene.String()
        district = graphene.String()

    school = graphene.Field(SchoolType)
    created = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        school, created = School.objects.update_or_create(
            id=validated_data.pop('id', None),
            defaults=validated_data
        )
        return CreateSchool(school=school, created=created)


class UserInput(graphene.InputObjectType):
    id = graphene.ID()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()
    password = graphene.String()


class StudentInput(graphene.InputObjectType):
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
    school_id = graphene.ID(name='school')
    primary_parent_id = graphene.ID(name='primaryParent')
    secondary_parent_id = graphene.ID(name='secondaryParent')


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
        school_id = graphene.ID(name='school')
        primary_parent_id = graphene.ID(name='primaryParent')
        secondary_parent_id = graphene.ID(name='secondaryParent')

    student = graphene.Field(StudentType)
    created = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, user, **validated_data):

        with transaction.atomic():
            # update request
            if user.get('id'):
                user_id = user.pop('id')
                User.objects.filter(id=user_id).update(**user)
                Student.objects.filter(user__id=user_id).update(**validated_data)
                student = Student.objects.get(user__id=user_id)
                student.refresh_from_db()
                student.save()

                LogEntry.objects.log_action(
                    user_id=info.context.user.id,
                    content_type_id=ContentType.objects.get_for_model(Student).pk,
                    object_id=student.user.id,
                    object_repr=f"{student.user.first_name} {student.user.last_name}",
                    action_flag=CHANGE
                )
                return CreateStudent(student=student, created=False)

            # create user and token
            user_object = User.objects.create_user(
                username=uuid.uuid4(),
                password='password',
                first_name=user['first_name'],
                last_name=user['last_name'],
                email=user.get('email')
            )
            Token.objects.get_or_create(user=user_object)

            # create account
            student = Student.objects.create(
                user=user_object,
                account_type='student',
                **validated_data
            )

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Student).pk,
                object_id=student.user.id,
                object_repr=f"{student.user.first_name} {student.user.last_name}",
                action_flag=ADDITION
            )
            return CreateStudent(student=student, created=True)


class CreateStudents(graphene.Mutation):
    class Arguments:
        students = graphene.List(StudentInput, required=True)

    students = graphene.List(StudentType)
    created = graphene.Boolean()

    @login_required
    @staticmethod
    def mutate(root, info, students):
        student_list = []
        for student_data in students:
            user = student_data.pop('user')
            with transaction.atomic():
                # update request
                if user.get('id'):
                    user_id = user.pop('id')
                    User.objects.filter(id=user_id).update(**user)
                    Student.objects.filter(user__id=user_id).update(**student_data)
                    student = Student.objects.get(user__id=user_id)
                    student.refresh_from_db()
                    student.save()

                    LogEntry.objects.log_action(
                        user_id=info.context.user.id,
                        content_type_id=ContentType.objects.get_for_model(Student).pk,
                        object_id=student.user.id,
                        object_repr=f"{student.user.first_name} {student.user.last_name}",
                        action_flag=CHANGE
                    )
                    return CreateStudent(student=student, created=False)

                # create user and token
                user_object = User.objects.create_user(
                    username=uuid.uuid4(),
                    password='password',
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    email=user.get('email')
                )
                Token.objects.get_or_create(user=user_object)

                # create account
                student = Student.objects.create(
                    user=user_object,
                    account_type='student',
                    **student_data
                )

                LogEntry.objects.log_action(
                    user_id=info.context.user.id,
                    content_type_id=ContentType.objects.get_for_model(Student).pk,
                    object_id=student.user.id,
                    object_repr=f"{student.user.first_name} {student.user.last_name}",
                    action_flag=ADDITION
                )
                student_list.append(student)
        return CreateStudents(students=student_list, created=True)


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
        relationship = RelationshipEnum()
        secondary_phone_number = graphene.String()

    parent = graphene.Field(ParentType)
    created = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # update request
            if user.get('id'):
                user_id = user.pop('id')
                User.objects.filter(id=user_id).update(**user)
                Parent.objects.filter(user__id=user_id).update(**validated_data)
                parent = Parent.objects.get(user__id=user_id)
                parent.refresh_from_db()
                parent.save()

                LogEntry.objects.log_action(
                    user_id=info.context.user.id,
                    content_type_id=ContentType.objects.get_for_model(Parent).pk,
                    object_id=parent.user.id,
                    object_repr=f"{parent.user.first_name} {parent.user.last_name}",
                    action_flag=CHANGE
                )
                return CreateParent(parent=parent, created=False)

            # create user and token
            user_object = User.objects.create_user(
                username=user.get('email', uuid.uuid4()),
                email=user.get('email', None),
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
            ParentNotificationSettings.objects.create(parent=parent)

            Email.objects.create(
                template_id=WELCOME_PARENT_TEMPLATE,
                recipient=parent.user.email,
                data={
                    'parent_name': parent.user.first_name,
                    'business_name': settings.BUSINESS_NAME,
                }
            )

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Parent).pk,
                object_id=parent.user.id,
                object_repr=f"{parent.user.first_name} {parent.user.last_name}",
                action_flag=ADDITION
            )
            return CreateParent(parent=parent, created=True)


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
    created = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # update request
            if user.get('id'):
                user_id = user.pop('id')
                User.objects.filter(id=user_id).update(**user)
                instructor = Instructor.objects.get(user__id=user_id)
                if 'subjects' in validated_data:
                    subjects = validated_data.pop('subjects')
                    instructor.subjects.set(subjects)
                    instructor.save()
                Instructor.objects.filter(user__id=user_id).update(**validated_data)
                instructor.refresh_from_db()

                LogEntry.objects.log_action(
                    user_id=info.context.user.id,
                    content_type_id=ContentType.objects.get_for_model(Instructor).pk,
                    object_id=instructor.user.id,
                    object_repr=f"{instructor.user.first_name} {instructor.user.last_name}",
                    action_flag=CHANGE
                )
                return CreateInstructor(instructor=instructor, created=False)

            # create user and token
            user_object = User.objects.create_user(
                username=user.get('email', uuid.uuid4()),
                email=user.get('email', None),
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

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Instructor).pk,
                object_id=instructor.user.id,
                object_repr=f"{instructor.user.first_name} {instructor.user.last_name}",
                action_flag=ADDITION
            )

            return CreateInstructor(instructor=instructor, created=True)


class CreateInstructorAvailability(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        instructor_id = graphene.ID(name='instructor')
        day_of_week = DayOfWeekEnum()
        start_time = graphene.Time()
        end_time = graphene.Time()

    instructor_availability = graphene.Field(InstructorAvailabilityType)
    created = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        instructor_avail, created = InstructorAvailability.objects.update_or_create(
            id=validated_data.pop('id', None),
            defaults=validated_data
        )
        return CreateInstructorAvailability(
            instructor_availability=instructor_avail,
            created=created
        )


class InstructorAvailabilityInput(graphene.InputObjectType):
    id = graphene.ID()
    instructor_id = graphene.ID(name='instructor')
    day_of_week = DayOfWeekEnum()
    start_time = graphene.Time()
    end_time = graphene.Time()


class CreateInstructorAvailabilities(graphene.Mutation):
    class Arguments:
        availabilities = graphene.List(InstructorAvailabilityInput, required=True)

    instructor_availabilities = graphene.List(InstructorAvailabilityType)

    @staticmethod
    def mutate(root, info, **validated_data):
        objs = [InstructorAvailability(**data) for data in validated_data['availabilities']]
        instructor_availabilities = InstructorAvailability.objects.bulk_create(objs)
        return CreateInstructorAvailabilities(
            instructor_availabilities=instructor_availabilities
        )


class DeleteInstructorAvailabilities(graphene.Mutation):
    class Arguments:
        availabilities = graphene.List(graphene.ID, required=True)

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        price_rule_objs = InstructorAvailability.objects.filter(
            id__in=validated_data['availabilities']
            )
        price_rule_objs.delete()
        return DeleteInstructorAvailabilities(deleted=True)


class CreateInstructorOOO(graphene.Mutation):
    class Arguments:
        instructor_id = graphene.ID(name='instructor')
        start_datetime = graphene.DateTime(required=True)
        end_datetime = graphene.DateTime(required=True)
        description = graphene.String()

    instructor_ooo = graphene.Field(InstructorOutOfOfficeType)

    @staticmethod
    def mutate(root, info, instructor_id, start_datetime, end_datetime, description=''):
        start_datetime = start_datetime.replace(tzinfo=None)
        end_datetime = end_datetime.replace(tzinfo=None)
        start_datetime_obj = pytz.timezone(
            'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
        end_datetime_obj = pytz.timezone(
            'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)
        instructor_ooo = InstructorOutOfOffice.objects.create(
            instructor_id=instructor_id,
            start_datetime=start_datetime_obj,
            end_datetime=end_datetime_obj,
            description=description,
        )
        return CreateInstructorOOO(instructor_ooo=instructor_ooo)


class DeleteInstructorOOO(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            ooo_obj = InstructorOutOfOffice.objects.get(id=validated_data.get('id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. InstructorOOO does not exist.')
        ooo_obj.delete()
        return DeleteInstructorOOO(deleted=True)


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
        google_auth_enabled = graphene.Boolean()

        # Admin fields
        admin_type = AdminTypeEnum(required=True)

    admin = graphene.Field(AdminType)
    created = graphene.Boolean()

    @staticmethod
    def mutate(root, info, user, **validated_data):
        with transaction.atomic():
            # update request
            if user.get('id'):
                user_id = user.pop('id')
                User.objects.filter(id=user_id).update(**user)
                Admin.objects.filter(user__id=user_id).update(**validated_data)
                admin = Admin.objects.get(user__id=user_id)
                if admin.admin_type == Admin.OWNER_TYPE:
                    user_object = User.objects.get(id=user_id)
                    user_object.is_staff = True
                    user_object.save()
                admin.refresh_from_db()
                admin.save()
                return CreateAdmin(admin=admin, created=False)

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


class CreateAccountNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(name='id')
        user_id = graphene.ID()
        title = graphene.String()
        body = graphene.String()
        important = graphene.Boolean()
        complete = graphene.Boolean()

    account_note = graphene.Field(AccountNoteType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        account_note, created = AccountNote.objects.update_or_create(
            id=validated_data.pop('note_id', None),
            defaults=validated_data
        )
        return CreateAccountNote(account_note=account_note, created=created)


class DeleteAccountNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(name='id')

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            note_obj = AccountNote.objects.get(id=validated_data.get('note_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. PriceRule does not exist.')
        note_obj.delete()
        return DeleteAccountNote(deleted=True)


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
            return RequestPasswordReset(status='failed', error_message='No such user exists.')

        token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

        email = Email.objects.create(
            template_id=RESET_PASSWORD_TEMPLATE,
            recipient=email,
            data={'username': user.first_name, 'token': token}
        )

        return RequestPasswordReset(status=email.status, error_message=email.response_body)


class ResetPassword(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID()
        username = graphene.ID()
        new_password = graphene.String(required=True)

    status = graphene.String()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        user_obj = User.objects.filter(
            Q(id = validated_data.get('user_id', None)) |
            Q(username = validated_data.get('username', None))
        )

        if user_obj.exists():
            status = 'success'
            user_obj = user_obj[0]
            user_obj.set_password(validated_data.get('new_password'))
            user_obj.save()
        else:
            status = 'failure'

        return ResetPassword(status=status)


class InviteStudent(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    status = graphene.String()
    error_message = graphene.String()

    @staticmethod
    def mutate(root, info, email):
        try:
            student = Student.objects.get(user__email=email)
        except Exception:
            return InviteStudent(status='failed', error_message='No such user exists.')

        token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

        invite_email = Email.objects.create(
            template_id=INVITE_STUDENT_TEMPLATE,
            recipient=email,
            data={
                'student_name': student.user.first_name,
                'parent_name': student.primary_parent.user.first_name,
                'token': token,
                'business_name': 'Stark Industries'
            }
        )

        return InviteStudent(status=invite_email.status, error_message=invite_email.response_body)


class InviteInstructor(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    status = graphene.String()
    error_message = graphene.String()

    @staticmethod
    def mutate(root, info, email):
        try:
            instructor = Instructor.objects.get(user__email=email)
        except Exception:
            return InviteInstructor(status='failed', error_message='No such user exists.')

        token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

        invite_email = Email.objects.create(
            template_id=INVITE_INSTRUCTOR_TEMPLATE,
            recipient=email,
            data={
                'instructor_name': instructor.user.first_name,
                'token': token,
                'business_name': 'Stark Industries'
            }
        )

        return InviteInstructor(status=invite_email.status, error_message=invite_email.response_body)


class Mutation(graphene.ObjectType):
    create_school = CreateSchool.Field()
    create_student = CreateStudent.Field()
    create_students = CreateStudents.Field()
    create_parent = CreateParent.Field()
    create_instructor = CreateInstructor.Field()
    create_admin = CreateAdmin.Field()
    create_account_note = CreateAccountNote.Field()

    create_instructor_availability = CreateInstructorAvailability.Field()
    create_instructor_availabilities = CreateInstructorAvailabilities.Field()
    delete_instructor_availabilities = DeleteInstructorAvailabilities.Field()
    create_instructor_ooo = CreateInstructorOOO.Field()

    # delete endpoints
    delete_instructor_ooo = DeleteInstructorOOO.Field()
    delete_account_note = DeleteAccountNote.Field()

    # Auth endpoints
    request_password_reset = RequestPasswordReset.Field()
    reset_password = ResetPassword.Field()

    # invite endpoints
    invite_student = InviteStudent.Field()
    invite_instructor = InviteInstructor.Field()

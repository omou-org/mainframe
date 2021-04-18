import graphene
from graphql import GraphQLError

from onboarding.models import Business
from onboarding.schema import BusinessType
from graphql_jwt.decorators import login_required, staff_member_required

import pandas as pd
from graphene_file_upload.scalars import Upload

from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from comms.models import Email, ParentNotificationSettings
from account.models import (
    School,
    Student,
    Parent,
    Instructor
)
from onboarding.schema import (
    autosize_ws_columns,
    create_accounts_template,
    workbook_to_base64
)

from mainframe.permissions import IsOwner
from django_graphene_permissions import permissions_checker

from tempfile import NamedTemporaryFile
import base64
from datetime import datetime
import re
import uuid

from django.conf import settings
from rest_framework.authtoken.models import Token
from comms.models import Email, ParentNotificationSettings
from comms.templates import (
    WELCOME_PARENT_TEMPLATE
)

EMAIL_PATTERN = re.compile("[^@]+@[^@]+\.[^@]+")
PHONE_PATTERN = re.compile("(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})")
ZIP_PATTERN = re.compile("(\d{5}(\-\d{4})?)$")
DATE_PATTERN = re.compile("\d{2}/\d{2}/\d{4}")

ACCOUNT_TO_REQUIRED_FIELDS = {
    'parent': ['First Name', 'Last Name', 'Email', 'Phone'],
    'student': ['First Name', 'Last Name', 'Email', "Parent's First Name", "Parent's Last Name", "Parent's Email"],
    'instructor': ['First Name', 'Last Name', 'Email', 'Phone', 'City', 'State', 'Zip Code']
} 


class CreateBusiness(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        address = graphene.String()

    business = graphene.Field(BusinessType)
    created = graphene.Boolean()

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, **validated_data):
        if (
            "name" in validated_data
            and Business.objects.filter(name=validated_data["name"]).count() > 0
        ):
            raise GraphQLError("Failed mutation. Business with name already exists.")

        business, created = Business.objects.update_or_create(
            id=validated_data.pop('id', None),
            defaults=validated_data
        )
        return CreateBusiness(business=business, created=created)


def check_required_fields(row, fields):
    for field_name in fields:
        if not row.get(field_name):
            return f"Missing required field '{field_name}'. Please fill it in."
    return None


# preliminary user checks
def check_account(row, account_type):
    # check required fields
    missing_field_error = check_required_fields(row, ACCOUNT_TO_REQUIRED_FIELDS[account_type])
    if missing_field_error:
        return missing_field_error

    # field type checks
    email = row.get('Email')
    phone = row.get('Phone')
    zipcode = row.get('Zip Code') or row.get('Zip Code (Optional)')
    birthday = row.get('Birthday MM/DD/YYYY (Optional)')
    primary_parent = row.get("Parent's Email")

    if not email or not EMAIL_PATTERN.search(email):
        return "The email is invalid. Please check the email again."

    if account_type is not "student" and (not phone or not PHONE_PATTERN.search(str(phone))):
        return "The phone number is invalid. Please check the phone number again."

    if account_type is not "student" and (not zipcode or not ZIP_PATTERN.search(str(zipcode))):
        return "The zip code is invalid. Please check the zip code again."

    if birthday and (not DATE_PATTERN.search(str(birthday)) or datetime.strptime(str(birthday), "%d/%m/%Y") >= datetime.now()):
        return "The birthday is invalid. Please check the birthday again."

    if primary_parent and not Parent.objects.filter(user__username=primary_parent).exists():
        return "No parent with that email exists. Please check the email agaim."

    return None


class UploadAccountsMutation(graphene.Mutation):
    class Arguments:
        accounts = Upload(required=True)

    total_success = graphene.Int()
    total_failure = graphene.Int()
    error_excel = graphene.String()

    @staticmethod
    @login_required
    @permissions_checker([IsOwner])
    def mutate(self, info, accounts, **kwargs):
        xls = pd.ExcelFile(accounts.read())

        # check all spreadsheets exist
        account_names = ['Parents', 'Students', 'Instructors']
        if not all(name in xls.sheet_names for name in account_names):
            raise GraphQLError("Please include all spreadsheets: "+account_names)

        # extract spreadsheets and skip first comment row
        parents_df = pd.read_excel(xls, sheet_name="Parents", header=1)
        students_df = pd.read_excel(xls, sheet_name="Students", header=1)
        instructors_df = pd.read_excel(xls, sheet_name="Instructors", header=1)

        # create parents
        parents_df = parents_df.where(pd.notnull(parents_df), None) # cast np.Nan to None
        parents_error_df = []
        for _index, row in parents_df.iloc[1:].iterrows():
            user_check = check_account(row, 'parent')
            if user_check:
                parents_error_df.append(row.to_dict())
                parents_error_df[-1]['Error Message'] = user_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row['Email'],
                        email=row['Email'],
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        password=User.objects.make_random_password()
                    )
                    user_object.save()
                    parent = Parent(
                        user=user_object,
                        account_type='parent',
                        phone_number=row['Phone'],
                        zipcode=row['Zip Code (Optional)']
                    )
                    parent.save()
            except Exception as e:
                parents_error_df.append(row.to_dict())
                parents_error_df[-1]['Error Message'] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
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
        

        # create Schools
        school_names = set(students_df['School (Optional)'].dropna().apply(lambda x: x.strip()))
        for name in school_names:
            if not School.objects.filter(name=name).exists():
                School.objects.create(name=name)


        # create students
        students_df = students_df.where(pd.notnull(students_df), None) # cast np.Nan to None
        students_error_df = []
        for _index, row in students_df.iloc[1:].iterrows():
            user_check = check_account(row, 'student')
            if user_check:
                students_error_df.append(row.to_dict())
                students_error_df[-1]['Error Message'] = user_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row['Email'],
                        email=row['Email'],
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        password=User.objects.make_random_password()
                    )
                    user_object.save()
                    student = Student(
                        user=user_object,
                        account_type='student',
                        grade=row.get('Grade Level (Optional)'),
                        school=None if not row.get('School (Optional)') else School.objects.get(name=row.get('School (Optional)')),
                        primary_parent=Parent.objects.get(user__username=row["Parent's Email"]),
                        birth_date=row.get('Birthday MM/DD/YYYY (Optional)')
                    )
                    student.save()
            except Exception as e:
                students_error_df.append(row.to_dict())
                students_error_df[-1]['Error Message'] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Student).pk,
                object_id=student.user.id,
                object_repr=f"{student.user.first_name} {student.user.last_name}",
                action_flag=ADDITION
            )


        # create instructors
        instructors_df = instructors_df.where(pd.notnull(instructors_df), None) # cast np.Nan to None
        instructors_error_df = []
        for index, row in instructors_df.iloc[1:].iterrows():
            user_check = check_account(row, 'instructor')
            if user_check:
                instructors_error_df.append(row.to_dict())
                instructors_error_df[-1]['Error Message'] = user_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row['Email'],
                        email=row['Email'],
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        password=User.objects.make_random_password()
                    )
                    user_object.save()
                    instructor = Instructor(
                        user=user_object,
                        account_type='instructor',
                        city=row['City'],
                        phone_number=row['Phone'],
                        state=row['State'],
                        zipcode=row['Zip Code']
                    )
                    instructor.save()
            except Exception as e:   
                instructors_error_df.append(row.to_dict())
                instructors_error_df[-1]['Error Message'] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Instructor).pk,
                object_id=instructor.user.id,
                object_repr=f"{instructor.user.first_name} {instructor.user.last_name}",
                action_flag=ADDITION
            )

        
        total = parents_df.shape[0]-1 + students_df.shape[0]-1 + instructors_df.shape[0]-1
        total_failure = len(parents_error_df) + len(students_error_df) + len(instructors_error_df)

        # construct error excel
        error_excel = ""
        if total_failure > 0:
            wb = create_accounts_template(show_errors=True)

            parents_ws = wb.get_sheet_by_name("Parents")
            parents_column_order = [cell.value for cell in parents_ws[2]]
            for index, row_error in enumerate(parents_error_df):
                for col in range(len(parents_column_order)):
                    parents_ws.cell(row=4+index, column=1+col).value = row_error[parents_column_order[col]]
            autosize_ws_columns(parents_ws)
            
            students_ws = wb.get_sheet_by_name("Students")
            students_column_order = [cell.value for cell in students_ws[2]]
            for index, row_error in enumerate(students_error_df):
                for col in range(len(students_column_order)):
                    students_ws.cell(row=4+index, column=1+col).value = row_error[students_column_order[col]]
            autosize_ws_columns(students_ws)

            instructors_ws = wb.get_sheet_by_name("Instructors")
            instructors_column_order = [cell.value for cell in instructors_ws[2]]
            for index, row_error in enumerate(instructors_error_df):
                for col in range(len(instructors_column_order)):
                    instructors_ws.cell(row=4+index, column=1+col).value = row_error[instructors_column_order[col]]
            autosize_ws_columns(instructors_ws)

            error_excel = workbook_to_base64(wb)

        return UploadAccountsMutation(
            total_success = total-total_failure,
            total_failure = total_failure,
            error_excel = error_excel
        )


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    upload_accounts = UploadAccountsMutation.Field()

import graphene
import stripe
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required
from graphene_file_upload.scalars import Upload

import decimal
import re
import pandas as pd
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django_graphene_permissions import permissions_checker

from mainframe.permissions import IsOwner
from rest_framework.authtoken.models import Token

from account.models import (
    Admin,
    School,
    Student,
    Parent,
    Instructor,
)
from account.schema import AdminType
from account.mutations import DayOfWeekEnum, UserInput
from course.models import (
    CourseCategory,
    Course,
    Enrollment,
)
from course.mutations import create_availabilities_and_sessions
from comms.models import Email, ParentNotificationSettings
from comms.templates import WELCOME_PARENT_TEMPLATE
from onboarding.models import Business, BusinessAvailability
from onboarding.schema import (
    BusinessType,
    autosize_ws_columns,
    create_account_templates,
    create_course_templates,
    create_enrollment_templates,
    workbook_to_base64,
)

COURSE_SHEET_NAME_PATTERN = re.compile("^(.+) - (\d+)$")
EMAIL_PATTERN = re.compile("[^@]+@[^@]+\.[^@]+")
PHONE_PATTERN = re.compile(
    "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
)
ZIP_PATTERN = re.compile("(\d{5}(\-\d{4})?)$")

ACCOUNT_SHEET_NAME_TO_REQUIRED_FIELDS = {
    "parent": ["First Name", "Last Name", "Email", "Phone"],
    "student": [
        "First Name",
        "Last Name",
        "Email",
        "Parent's First Name",
        "Parent's Last Name",
        "Parent's Email",
    ],
    "instructor": [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "City",
        "State",
        "Zip Code",
    ],
}

COURSE_SHEET_NAME_TO_REQUIRED_FIELDS = {
    "subjects": ["Subjects", "Description"],
    "courses": [
        "Course Name",
        "Instructor",
        "Instructor Confirmed? (Y/N)",
        "Subject",
        "Course Description",
        "Academic Level",
        "Room Location",
        "Total Tuition",
        "Enrollment Capacity (>=4)",
        "Start Date",
        "End Date",
        "Session Day 1",
        "Start Time 1",
        "End Time 1",
        "Session Day 2",
        "Start Time 2",
        "End Time 2",
        "Session Day 3",
        "Start Time 3",
        "End Time 3",
        "Session Day 4",
        "Start Time 4",
        "End Time 4",
        "Session Day 5",
        "Start Time 5",
        "End Time 5",
    ],
    "courses_minimum": [
        "Course Name",
        "Instructor",
        "Instructor Confirmed? (Y/N)",
        "Subject",
        "Course Description",
        "Academic Level",
        "Room Location",
        "Total Tuition",
        "Enrollment Capacity (>=4)",
        "Start Date",
        "End Date",
        "Session Day 1",
        "Start Time 1",
        "End Time 1",
    ],
}


class CreateOwnerInput(graphene.InputObjectType):
    user = UserInput(required=True)
    address = graphene.String()
    city = graphene.String()
    phone_number = graphene.String()
    state = graphene.String()
    zipcode = graphene.String()


class BusinessAvailabilityInput(graphene.InputObjectType):
    day_of_week = DayOfWeekEnum(require=True)
    start_time = graphene.Time(require=True)
    end_time = graphene.Time(require=True)


class CreateBusinessInput(graphene.InputObjectType):
    name = graphene.String(require=True)
    phone_number = graphene.String(require=True)
    email = graphene.String(require=True)
    address = graphene.String(require=True)
    availabilities = graphene.List(BusinessAvailabilityInput, require=True)


class UpdateBusiness(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        phone_number = graphene.String()
        email = graphene.String()
        address = graphene.String()
        availabilities = graphene.List(BusinessAvailabilityInput)

    business = graphene.Field(BusinessType)
    updated = graphene.Boolean()

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, **validated_data):
        user_id = info.context.user.id
        admin = Admin.objects.get(user__id=user_id)

        if (
            "name" in validated_data
            and Business.objects.filter(name=validated_data["name"])
            .exclude(id=admin.business.id)
            .exists()
        ):
            raise GraphQLError("Failed mutation. Business with name already exists.")

        with transaction.atomic():
            # update business
            business_object, updated = Business.objects.update_or_create(
                id=admin.business.id, defaults=validated_data
            )

            # remove old availabilities and create new ones
            if "availabilities" in validated_data:
                availabilities_dict_list = validated_data.pop("availabilities")
                if availabilities_dict_list:
                    BusinessAvailability.objects.filter(
                        business=business_object
                    ).delete()
                    for availability_dict in availabilities_dict_list:
                        BusinessAvailability.objects.create(
                            business=business_object, **availability_dict
                        )

            return UpdateBusiness(business=business_object, updated=updated)


class CreateOwnerAndBusiness(graphene.Mutation):
    class Arguments:
        owner = CreateOwnerInput()
        business = CreateBusinessInput()

    owner = graphene.Field(AdminType)
    business = graphene.Field(BusinessType)
    created = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        with transaction.atomic():
            owner_dict = validated_data["owner"]
            user_dict = owner_dict.pop("user")
            business_dict = validated_data["business"]
            availabilities_dict_list = business_dict.pop("availabilities")

            # create business
            if Business.objects.filter(name=business_dict["name"]).exists():
                raise GraphQLError(
                    "Failed mutation. Business with name already exists."
                )

            business_object = Business.objects.create(**business_dict)
            for availability_dict in availabilities_dict_list:
                BusinessAvailability.objects.create(
                    business=business_object, **availability_dict
                )
            # create user and token
            user_object = User.objects.create_user(
                email=user_dict["email"],
                username=user_dict["email"],
                password=user_dict["password"],
                first_name=user_dict["first_name"],
                last_name=user_dict["last_name"],
                is_staff=True,
            )
            Token.objects.get_or_create(user=user_object)
            # create owner
            owner_object = Admin.objects.create(
                user=user_object,
                account_type="admin",
                admin_type=Admin.OWNER_TYPE,
                business=business_object,
                **owner_dict,
            )
            return CreateOwnerAndBusiness(
                owner=owner_object, business=business_object, created=True
            )


def check_required_fields(row, fields):
    for field_name in fields:
        if not row.get(field_name):
            return f"Missing required field '{field_name}'. Please fill it in."
    return None


# preliminary account spreadsheet row checks
def check_account_sheet_row(row, account_type, business_id=None):
    # check required fields
    missing_field_error = check_required_fields(
        row, ACCOUNT_SHEET_NAME_TO_REQUIRED_FIELDS[account_type]
    )
    if missing_field_error:
        return missing_field_error

    # field type checks
    email = row.get("Email")
    phone = row.get("Phone")
    zipcode = row.get("Zip Code") or row.get("Zip Code (Optional)")
    birthday = row.get("Birthday MM/DD/YYYY (Optional)")
    primary_parent = row.get("Parent's Email")

    if not email or not EMAIL_PATTERN.search(email):
        return "The email is invalid. Please check the email again."

    if account_type != "student":
        if not phone or not PHONE_PATTERN.search(str(phone)):
            return "The phone number is invalid. Please check the phone number again."

        if account_type == "parent" and not zipcode:
            pass
        elif not zipcode or not ZIP_PATTERN.search(str(zipcode)):
            return "The zip code is invalid. Please check the zip code again."

    if birthday and (type(birthday) != datetime or birthday >= datetime.now()):
        return "The birthday is invalid. Please check the birthday again."

    if (
        primary_parent
        and not Parent.objects.filter(
            business__id=business_id, user__username=primary_parent
        ).exists()
    ):
        return "No parent with that email exists. Please check the email agaim."

    return None


# preliminary course spreadsheet row checks
def check_course_sheet_row(
    row, model_type, business_id=None, dropdown_subject_names=set()
):
    # check required fields
    missing_field_error = check_required_fields(
        row, COURSE_SHEET_NAME_TO_REQUIRED_FIELDS[model_type]
    )
    if missing_field_error:
        return missing_field_error

    if model_type == "courses_minimum":

        if not Instructor.objects.filter(
            business__id=business_id, user__email=row.get("Instructor")
        ).exists():
            return "The instuctor listed was not found. Please either add the instructor or change the instructor."

        if row.get("Instructor Confirmed? (Y/N)") not in ["Y", "N"]:
            return 'There\'s been an invalid character in column C. Please change it to either "Y" or "N."'

        if row.get("Subject") not in dropdown_subject_names:
            return "There's been an invalid subject found in column D. Please change it to one of the subjects in the dropdown menu."

        if row.get("Academic Level") not in [
            "Elementary",
            "Middle School",
            "High School",
            "College",
        ]:
            return "There's been an invalid academic subject found in column F. Please change it to one of the academic levels in the dropdown menu."

        if (
            not str(row.get("Enrollment Capacity (>=4)")).isdigit()
            or int(row.get("Enrollment Capacity (>=4)")) < 4
        ):
            return "There's an invalid Enrollment Capacity. Please check that at least 4 students can enroll in the course."

        start_date = row.get("Start Date")
        end_date = row.get("End Date")

        if type(start_date) != datetime or type(end_date) != datetime:
            return "The start / end date is an invalid date. Please change it to a valid date."

        if end_date < start_date:
            return "The start date is after the end date. Please change the start/end dates to valid dates."

        if start_date.strftime("%A") != row.get("Session Day 1"):
            return "The start date day of week is not on the same as session day 1."

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
        owner = Admin.objects.get(user=info.context.user)
        business_id = owner.business.id
        business = Business.objects.get(id=business_id)

        xls = pd.ExcelFile(accounts.read())

        # check all spreadsheets exist
        account_names = ["Parents", "Students", "Instructors"]
        if not all(name in xls.sheet_names for name in account_names):
            raise GraphQLError("Please include all spreadsheets: " + str(account_names))

        # extract spreadsheets and skip first comment row
        parents_df = pd.read_excel(xls, sheet_name="Parents", header=1)
        students_df = pd.read_excel(xls, sheet_name="Students", header=1)
        instructors_df = pd.read_excel(xls, sheet_name="Instructors", header=1)

        # check all column headers present
        parent_ws_missing_columns = set(
            ACCOUNT_SHEET_NAME_TO_REQUIRED_FIELDS["parent"]
        ) - set(parents_df.columns.values)
        if len(parent_ws_missing_columns) > 0:
            raise GraphQLError(
                "Missing columns in parents worksheet: "
                + str(parent_ws_missing_columns)
            )

        instructor_ws_missing_columns = set(
            ACCOUNT_SHEET_NAME_TO_REQUIRED_FIELDS["instructor"]
        ) - set(instructors_df.columns.values)
        if len(instructor_ws_missing_columns) > 0:
            raise GraphQLError(
                "Missing columns in instructors workshet: "
                + str(instructor_ws_missing_columns)
            )

        student_ws_missing_columns = set(
            ACCOUNT_SHEET_NAME_TO_REQUIRED_FIELDS["student"]
        ) - set(students_df.columns.values)
        if len(student_ws_missing_columns) > 0:
            raise GraphQLError(
                "Missing columns in students workshet: "
                + str(student_ws_missing_columns)
            )

        # create parents
        parents_df = parents_df.dropna(how="all")
        parents_df = parents_df.where(
            pd.notnull(parents_df), None
        )  # cast np.Nan to None
        parents_error_df = []
        for _index, row in parents_df.iloc[1:].iterrows():
            required_fields_check = check_account_sheet_row(row, "parent")
            if required_fields_check:
                parents_error_df.append(row.to_dict())
                parents_error_df[-1]["Error Message"] = required_fields_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row["Email"],
                        email=row["Email"],
                        first_name=row["First Name"],
                        last_name=row["Last Name"],
                        password=User.objects.make_random_password(),
                    )
                    user_object.save()
                    parent = Parent(
                        user=user_object,
                        business=business,
                        account_type="parent",
                        phone_number=row["Phone"],
                        zipcode=row.get("Zip Code (Optional)"),
                    )
                    parent.save()
            except Exception as e:
                parents_error_df.append(row.to_dict())
                parents_error_df[-1]["Error Message"] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
            ParentNotificationSettings.objects.create(parent=parent)
            Email.objects.create(
                template_id=WELCOME_PARENT_TEMPLATE,
                recipient=parent.user.email,
                data={
                    "parent_name": parent.user.first_name,
                    "business_name": settings.BUSINESS_NAME,
                },
            )
            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Parent).pk,
                object_id=parent.user.id,
                object_repr=f"{parent.user.first_name} {parent.user.last_name}",
                action_flag=ADDITION,
            )

        # create Schools
        school_names = set(
            students_df["School (Optional)"].dropna().apply(lambda x: x.strip())
        )
        for name in school_names:
            if not School.objects.filter(name=name).exists():
                School.objects.create(name=name)

        # create students
        students_df = students_df.dropna(how="all")
        students_df = students_df.where(
            pd.notnull(students_df), None
        )  # cast np.Nan to None
        students_error_df = []
        for _index, row in students_df.iloc[1:].iterrows():
            required_fields_check = check_account_sheet_row(row, "student", business_id)
            if required_fields_check:
                students_error_df.append(row.to_dict())
                students_error_df[-1]["Error Message"] = required_fields_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row["Email"],
                        email=row["Email"],
                        first_name=row["First Name"],
                        last_name=row["Last Name"],
                        password=User.objects.make_random_password(),
                    )
                    user_object.save()
                    student = Student(
                        user=user_object,
                        business=business,
                        account_type="student",
                        grade=row.get("Grade Level (Optional)"),
                        school=None
                        if not row.get("School (Optional)")
                        else School.objects.get(name=row.get("School (Optional)")),
                        primary_parent=Parent.objects.get(
                            user__username=row["Parent's Email"]
                        ),
                        birth_date=row.get("Birthday MM/DD/YYYY (Optional)"),
                    )
                    student.save()
            except Exception as e:
                students_error_df.append(row.to_dict())
                students_error_df[-1]["Error Message"] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Student).pk,
                object_id=student.user.id,
                object_repr=f"{student.user.first_name} {student.user.last_name}",
                action_flag=ADDITION,
            )

        # create instructors
        instructors_df = instructors_df.dropna(how="all")
        instructors_df = instructors_df.where(
            pd.notnull(instructors_df), None
        )  # cast np.Nan to None
        instructors_error_df = []
        for index, row in instructors_df.iloc[1:].iterrows():
            required_fields_check = check_account_sheet_row(row, "instructor")
            if required_fields_check:
                instructors_error_df.append(row.to_dict())
                instructors_error_df[-1]["Error Message"] = required_fields_check
                continue
            try:
                with transaction.atomic():
                    user_object = User(
                        username=row["Email"],
                        email=row["Email"],
                        first_name=row["First Name"],
                        last_name=row["Last Name"],
                        password=User.objects.make_random_password(),
                    )
                    user_object.save()
                    instructor = Instructor(
                        user=user_object,
                        business=business,
                        account_type="instructor",
                        city=row["City"],
                        phone_number=row["Phone"],
                        state=row["State"],
                        zipcode=row["Zip Code"],
                    )
                    instructor.save()
            except Exception as e:
                instructors_error_df.append(row.to_dict())
                instructors_error_df[-1]["Error Message"] = str(e)
                continue

            Token.objects.get_or_create(user=user_object)
            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Instructor).pk,
                object_id=instructor.user.id,
                object_repr=f"{instructor.user.first_name} {instructor.user.last_name}",
                action_flag=ADDITION,
            )

        total = (
            parents_df.shape[0]
            - 1
            + students_df.shape[0]
            - 1
            + instructors_df.shape[0]
            - 1
        )
        total_failure = (
            len(parents_error_df) + len(students_error_df) + len(instructors_error_df)
        )

        # construct error excel
        error_excel = ""
        if total_failure > 0:
            wb = create_account_templates(show_errors=True)

            parents_ws = wb.get_sheet_by_name("Parents")
            parents_column_order = [cell.value for cell in parents_ws[2]]
            for index, row_error in enumerate(parents_error_df):
                for col in range(len(parents_column_order)):
                    parents_ws.cell(row=4 + index, column=1 + col).value = row_error[
                        parents_column_order[col]
                    ]
            autosize_ws_columns(parents_ws)

            students_ws = wb.get_sheet_by_name("Students")
            students_column_order = [cell.value for cell in students_ws[2]]
            for index, row_error in enumerate(students_error_df):
                for col in range(len(students_column_order)):
                    students_ws.cell(row=4 + index, column=1 + col).value = row_error[
                        students_column_order[col]
                    ]
            autosize_ws_columns(students_ws)

            instructors_ws = wb.get_sheet_by_name("Instructors")
            instructors_column_order = [cell.value for cell in instructors_ws[2]]
            for index, row_error in enumerate(instructors_error_df):
                for col in range(len(instructors_column_order)):
                    instructors_ws.cell(
                        row=4 + index, column=1 + col
                    ).value = row_error[instructors_column_order[col]]
            autosize_ws_columns(instructors_ws)

            error_excel = workbook_to_base64(wb)

        return UploadAccountsMutation(
            total_success=total - total_failure,
            total_failure=total_failure,
            error_excel=error_excel,
        )


class UploadCoursesMutation(graphene.Mutation):
    class Arguments:
        courses = Upload(required=True)

    total_success = graphene.Int()
    total_failure = graphene.Int()
    error_excel = graphene.String()

    @staticmethod
    @login_required
    @permissions_checker([IsOwner])
    def mutate(self, info, courses, **kwargs):
        owner = Admin.objects.get(user=info.context.user)
        business_id = owner.business.id
        business = Business.objects.get(id=business_id)

        xls = pd.ExcelFile(courses.read())

        # check all spreadsheets exist
        spreadsheet_names = ["Step 1 - Subject Categories", "Step 2 - Classes"]
        if not all(name in xls.sheet_names for name in spreadsheet_names):
            raise GraphQLError(
                "Please include all spreadsheets: " + str(spreadsheet_names)
            )

        # extract spreadsheets and skip first comment row
        subjects_df = pd.read_excel(
            xls, sheet_name="Step 1 - Subject Categories", header=1
        )
        courses_df = pd.read_excel(xls, sheet_name="Step 2 - Classes", header=1)

        # check all column headers present
        subjects_ws_missing_columns = set(
            COURSE_SHEET_NAME_TO_REQUIRED_FIELDS["subjects"]
        ) - set(subjects_df.columns.values)
        if len(subjects_ws_missing_columns) > 0:
            raise GraphQLError(
                "Missing columns in subjects worksheet: "
                + str(subjects_ws_missing_columns)
            )

        courses_ws_missing_columns = set(
            COURSE_SHEET_NAME_TO_REQUIRED_FIELDS["courses"]
        ) - set(courses_df.columns.values)
        if len(courses_ws_missing_columns) > 0:
            raise GraphQLError(
                "Missing columns in courses workshet: "
                + str(courses_ws_missing_columns)
            )

        # create subjects
        subjects_df = subjects_df.dropna(how="all")
        subjects_df = subjects_df.where(
            pd.notnull(subjects_df), None
        )  # cast np.Nan to None
        subjects_error_df = []
        for _index, row in subjects_df.iloc[1:].iterrows():
            required_fields_check = check_course_sheet_row(row, "subjects")
            if required_fields_check:
                subjects_error_df.append(row.to_dict())
                subjects_error_df[-1]["Error Message"] = required_fields_check
                continue

            # include valid subjects in error file for courses that rely on them
            subjects_error_df.append(row.to_dict())
            subjects_error_df[-1]["Error Message"] = ""
            try:
                # ignore subjects that already exist
                if CourseCategory.objects.filter(name=row.get("Subjects")).exists():
                    continue

                course_category = CourseCategory(
                    name=row.get("Subjects"), description=row.get("Description")
                )
                course_category.save()
            except Exception as e:
                subjects_error_df[-1]["Error Message"] = str(e)
                continue

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(CourseCategory).pk,
                object_id=course_category.id,
                object_repr=course_category.name,
                action_flag=ADDITION,
            )

        # create courses
        def extract_from_parenthesis(s):
            if s:
                return s[s.find("(") + 1 : s.find(")")]
            else:
                return s

        academic_level_to_enum_str = {
            "Elementary": "elementary_lvl",
            "Middle School": "middle_lvl",
            "High School": "high_lvl",
            "College": "college_lvl",
        }

        courses_df = courses_df.dropna(how="all")
        courses_df = courses_df.where(
            pd.notnull(courses_df), None
        )  # cast np.Nan to None

        courses_error_df = []
        dropdown_subject_names = set(subjects_df["Subjects"])
        for _index, row in courses_df.iloc[1:].iterrows():
            orig_instructor_field = row["Instructor"]
            row["Instructor"] = extract_from_parenthesis(row["Instructor"])

            required_fields_check = check_course_sheet_row(
                row, "courses_minimum", business_id, dropdown_subject_names
            )
            if required_fields_check:
                courses_error_df.append(row.to_dict())
                courses_error_df[-1]["Instructor"] = orig_instructor_field
                courses_error_df[-1]["Error Message"] = required_fields_check
                continue
            try:
                course = Course(
                    business=business,
                    title=row.get("Course Name"),
                    course_category=CourseCategory.objects.get(name=row.get("Subject")),
                    description=row.get("Course Description"),
                    total_tuition=row.get("Total Tuition"),
                    instructor=Instructor.objects.get(
                        user__email=row.get("Instructor")
                    ),
                    is_confirmed=row.get("Instructor Confirmed? (Y/N)") == "Y",
                    academic_level=academic_level_to_enum_str[
                        row.get("Academic Level")
                    ],
                    room=row.get("Room Location"),
                    start_date=row.get("Start Date"),
                    end_date=row.get("End Date"),
                    course_type="class",
                    max_capacity=int(row.get("Enrollment Capacity (>=4)")),
                )
                course.save()
            except Exception as e:
                courses_error_df.append(row.to_dict())
                courses_error_df[-1]["Instructor"] = orig_instructor_field
                courses_error_df[-1]["Error Message"] = str(e)
                continue

            # parse course availabilities
            availabilities = [
                {
                    "day_of_week": row.get(f"Session Day {i+1}").lower(),
                    "start_time": row.get(f"Start Time {i+1}"),
                    "end_time": row.get(f"End Time {i+1}"),
                }
                for i in range(5)
                if row.get(f"Session Day {i+1}")
            ]
            # populate sessions and availabilities
            course_availabilities = create_availabilities_and_sessions(
                course, availabilities
            )

            # calculate total hours across all sessions
            total_hours = decimal.Decimal("0.0")
            for availability in course_availabilities:
                duration_sec = (
                    datetime.combine(date.min, availability.end_time)
                    - datetime.combine(date.min, availability.start_time)
                ).seconds
                duration_hours = decimal.Decimal(duration_sec) / (60 * 60)
                total_hours += duration_hours * availability.num_sessions

            course.hourly_tuition = course.total_tuition / total_hours
            course.save()
            course.refresh_from_db()

            LogEntry.objects.log_action(
                user_id=info.context.user.id,
                content_type_id=ContentType.objects.get_for_model(Course).pk,
                object_id=course.id,
                object_repr=course.title,
                action_flag=ADDITION,
            )

        total = subjects_df.shape[0] - 1 + courses_df.shape[0] - 1
        total_failure = sum(
            1 for row in subjects_error_df if row["Error Message"]
        ) + len(courses_error_df)

        # construct error excel
        error_excel = ""
        if total_failure > 0:
            wb = create_course_templates(business_id, show_errors=True)

            categories_ws = wb.get_sheet_by_name("Step 1 - Subject Categories")
            categories_column_order = [cell.value for cell in categories_ws[2]]
            for index, row_error in enumerate(subjects_error_df):
                for col in range(len(categories_column_order)):
                    categories_ws.cell(row=4 + index, column=1 + col).value = row_error[
                        categories_column_order[col]
                    ]
            autosize_ws_columns(categories_ws)

            course_ws = wb.get_sheet_by_name("Step 2 - Classes")
            course_column_order = [cell.value for cell in course_ws[2]]
            for index, row_error in enumerate(courses_error_df):
                for col in range(len(course_column_order)):
                    course_ws.cell(row=4 + index, column=1 + col).value = row_error[
                        course_column_order[col]
                    ]
            autosize_ws_columns(course_ws)

            error_excel = workbook_to_base64(wb)

        return UploadCoursesMutation(
            total_success=total - total_failure,
            total_failure=total_failure,
            error_excel=error_excel,
        )


class UploadEnrollmentsMutation(graphene.Mutation):
    class Arguments:
        enrollments = Upload(required=True)

    total_success = graphene.Int()
    total_failure = graphene.Int()
    error_excel = graphene.String()

    @staticmethod
    @login_required
    @permissions_checker([IsOwner])
    def mutate(self, info, enrollments, **kwargs):
        owner = Admin.objects.get(user=info.context.user)
        business_id = owner.business.id
        error_excel = ""
        wb = create_enrollment_templates(business_id, show_errors=True)
        overall_total = 0
        total_errors = 0

        xls = pd.ExcelFile(enrollments.read())

        # check all course spreadsheets reflect courses that exist
        def isValidCourseSheetName(sheet_name):
            if sheet_name == "Student Roster (hidden)":
                return True
            # check sheet name matches "name - id"
            valid_sheet_name = COURSE_SHEET_NAME_PATTERN.search(sheet_name)

            if not valid_sheet_name:
                return False
            # check id and title exist in database
            course_title, course_id = valid_sheet_name.groups()
            if (
                not Course.objects.business(business_id)
                .filter(id=course_id, title=course_title)
                .exists()
            ):
                return False
            return True

        invalid_sheet_names = [
            sheet_name
            for sheet_name in xls.sheet_names
            if not isValidCourseSheetName(sheet_name)
        ]
        if invalid_sheet_names:
            raise GraphQLError(
                "Invalid spreadsheet names in Enrollments worksheet: "
                + str(invalid_sheet_names)
            )

        # upload enrollments
        for sheet_name in wb.sheetnames:
            if sheet_name == "Student Roster (hidden)":
                continue

            # extract spreadsheet and use 8th row (7th 0-indexed) for header, skipping all previous rows
            enrollment_df = pd.read_excel(
                xls, sheet_name=sheet_name, skiprows=7, header=0, usecols=[0]
            )

            # check students enrolled columns exists
            enrollment_ws_missing_columns = {"Students Enrolled"} - set(
                enrollment_df.columns.values
            )
            if len(enrollment_ws_missing_columns) > 0:
                raise GraphQLError(
                    f"Missing columns in enrollments worksheet ({sheet_name}): "
                    + str(enrollment_ws_missing_columns)
                )

            # extract the course
            course_title, course_id = COURSE_SHEET_NAME_PATTERN.search(
                sheet_name
            ).groups()
            course = (
                Course.objects.business(business_id)
                .filter(id=int(course_id), title=course_title)
                .first()
            )

            # create enrollments
            enrollment_df = enrollment_df.dropna(how="all")
            enrollment_error_df = []
            for _index, row in enrollment_df.iloc[0:].iterrows():
                entry = row["Students Enrolled"]
                student_email = (
                    entry[entry.find("(") + 1 : entry.find(")")]
                    if entry.find("(") and entry.find(")")
                    else ""
                )
                if not Student.objects.filter(user__email=student_email).exists():
                    enrollment_error_df.append(row.to_dict())
                    enrollment_error_df[-1][
                        "Error Message"
                    ] = "No student with that email exists. Please check the entry again."
                    continue

                try:
                    with transaction.atomic():
                        student = Student.objects.get(user__email=student_email)
                        enrollment_object = Enrollment.objects.create(
                            student=student,
                            course=course,
                            invite_status=Enrollment.SENT,
                        )
                except Exception as e:
                    enrollment_error_df.append(row.to_dict())
                    enrollment_error_df[-1]["Error Message"] = str(e)
                    continue
            total = enrollment_df.shape[0]
            errors = len(enrollment_error_df)
            if errors > 0:
                enrollments_ws = wb.get_sheet_by_name(sheet_name)
                enrollments_column_order = [cell.value for cell in enrollments_ws[8]][
                    :2
                ]

                for index, row_error in enumerate(enrollment_error_df):
                    for col in range(len(enrollments_column_order)):
                        enrollments_ws.cell(
                            row=9 + index, column=1 + col
                        ).value = row_error[enrollments_column_order[col]]
                autosize_ws_columns(enrollments_ws)
            overall_total += total
            total_errors += errors

        if total_errors > 0:
            error_excel = workbook_to_base64(wb)

        return UploadEnrollmentsMutation(
            total_success=overall_total - total_errors,
            total_failure=total_errors,
            error_excel=error_excel,
        )


class StripeOnboarding(graphene.Mutation):
    class Arguments:
        refresh_url_param = graphene.String(required=True)
        return_url_param = graphene.String(required=True)

    onboarding_url = graphene.String()

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, refresh_url_param, return_url_param):
        user_id = info.context.user.id
        admin = Admin.objects.get(user__id=user_id)
        stripe.api_key = settings.STRIPE_API_KEY

        account = stripe.Account.create(type='standard', email=admin.user.email)
        account_links = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f'{settings.BASE_URL}/{refresh_url_param}',
            return_url=f'{settings.BASE_URL}/{return_url_param}',
            type='account_onboarding'
        )

        return StripeOnboarding(onboarding_url=account_links.url)


class Mutation(graphene.ObjectType):
    update_business = UpdateBusiness.Field()
    create_owner_and_business = CreateOwnerAndBusiness.Field()
    upload_accounts = UploadAccountsMutation.Field()
    upload_courses = UploadCoursesMutation.Field()
    upload_enrollments = UploadEnrollmentsMutation.Field()
    stripe_onboarding = StripeOnboarding.Field()

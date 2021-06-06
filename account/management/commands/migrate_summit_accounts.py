from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import pandas as pd
import uuid
import math

from account.models import Student
from account.models import Parent
from account.models import Note

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    bad_rows = []
    rowNum = 1

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Successfully called"))
        dataframe = self.read_data_from_file("data/summit_student.csv")

        self.insert_accounts(dataframe)
        print(str(self.bad_rows))

    def read_data_from_file(self, file_name):
        return pd.read_csv(file_name)

    def insert_accounts(self, dataframe):
        # add school to student

        # add primary parent & add relationship from student to parent

        # parent info:
        # phone #
        # secondary phone #
        # first name
        # last name
        # city, address, ZIP
        # email

        # Make note obj
        # add relationship from note to student

        # add try/catch and print error lines to console

        # TODO: check objects created in database

        for row in dataframe.itertuples():
            print(str(self.rowNum))

            parent = self.create_parent(row)
            student_user = self.create_student(row, parent)
            self.create_note(row, student_user)

            self.rowNum += 1

    def translate_gender(self, gender):
        if str(gender) == "Female":
            return "F"
        elif str(gender) == "Male":
            return "M"
        else:
            return "U"

    def get_first_name_last_name_from_field(self, name_field):
        words = name_field.split()

        if len(words) == 0:
            raise Exception("improper name field")

        if len(words) == 1:
            return words[0], ""
        return " ".join(words[:-1]), words[-1]

    def create_parent(self, row):
        if isinstance(row[15], float):
            return None

        try:
            (
                parent_first_name,
                parent_last_name,
            ) = self.get_first_name_last_name_from_field(row[15])

            username = row[18]
            email = row[18]
            if isinstance(row[18], float):
                username = uuid.uuid4()
                email = ""
            else:
                queryset = Parent.objects.filter(user__email=email)
                if queryset.count() > 0:
                    return queryset[0]

            with transaction.atomic():
                parent_user = User.objects.create_user(
                    username=username,
                    password="password",
                    first_name=parent_first_name,
                    last_name=parent_last_name,
                    email=email,
                )

                parent = Parent.objects.create(
                    user=parent_user,
                    user_uuid=parent_user.username,
                    address=row[22],
                    city=row[23],
                    phone_number=row[16],
                    state=row[24],
                    zipcode=row[25],
                    secondary_phone_number=row[17],
                    account_type="PARENT",
                )

                parent.save()

            return parent
        except Exception as e:
            print("ERROR: creating parent obj", row)
            print(e)
            self.bad_rows.append(str(self.rowNum) + " parent")
            return None

    def create_student(self, row, parent):
        try:
            student_user = User.objects.create_user(
                username=uuid.uuid4(),
                password="password",
                first_name=row[3],
                last_name=row[4],
            )

            Token.objects.get_or_create(user=student_user)

            grade = row[10]

            if math.isnan(float(grade)):
                student = Student.objects.create(
                    user=student_user,
                    gender=self.translate_gender(row[9]),
                    user_uuid=row[2],
                    address=row[22],
                    city=row[23],
                    state=row[24],
                    zipcode=row[25],
                    school=row[11],
                    primary_parent=parent,
                    account_type="STUDENT",
                )
            else:
                student = Student.objects.create(
                    user=student_user,
                    gender=self.translate_gender(row[9]),
                    user_uuid=row[2],
                    address=row[22],
                    city=row[23],
                    state=row[24],
                    zipcode=row[25],
                    school=row[11],
                    primary_parent=parent,
                    grade=row[10],
                    account_type="STUDENT",
                )

            student.save()

            return student_user
        except Exception as e:
            print("ERROR: creating student obj", row)
            print(e)
            self.bad_rows.append(str(self.rowNum) + " student")
            return None

    def create_note(self, row, student_user):
        try:
            note = Note.objects.create(user=student_user, body=row[26])

            note.save()
        except Exception as e:
            print("ERROR: creating note obj", row)
            print(e)
            self.bad_rows.append(str(self.rowNum) + " note")
        return None


# Index to column name mapping:
# 1 "Criteria"
# 2 "Student ID"
# 3 "First Name"
# 4 "Last Name"
# 5 "Other Name"
# 6 "Student"
# 7 "Enroll Date"
# 8 "Status"
# 9 "Gender"
# 10 "Grade"
# 11 "School"
# 12 "Updated Date"
# 13 Updated by"
# 14 "Title"
# 15 "Parent"
# 16 "H Phone"
# 17 "C Phone"
# 18 "E-mail address"
# 19 "Emergency"
# 20 "E Phone"
# 21 "Ref By"
# 22 "Address"
# 23 "City"
# 24 "State"
# 25 "Zip"
# 26 "Note"

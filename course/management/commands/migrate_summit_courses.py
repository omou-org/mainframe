from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import pandas as pd
import uuid
import arrow

from account.models import Instructor
from course.models import Course
from course.models import CourseCategory
from course.models import CourseNote

from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    bad_rows = []
    rowNum = 1

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Successfully called"))
        dataframe = self.read_data_from_file("data/summit_classes.csv")

        self.insert_courses(dataframe)

    def read_data_from_file(self, file_name):
        return pd.read_csv(file_name)

    def insert_courses(self, dataframe):
        for row in dataframe.itertuples():
            print(str(self.rowNum), row)

            instructor = self.create_instructor(row)
            self.create_course(row, instructor)
            self.rowNum += 1

    def create_instructor(self, row):
        if isinstance(row[3], float):
            return None
        try:
            tokens = row[3].split(" ")
            first_name = tokens[1]
            last_name = ""
            if len(tokens) > 2:
                last_name = tokens[2]

            queryset = Instructor.objects.filter(user__first_name=first_name)
            if queryset.count() > 0:
                return queryset[0]

            with transaction.atomic():
                instructor_user = User.objects.create_user(
                    username=uuid.uuid4(),
                    password="password",
                    first_name=first_name,
                    last_name=last_name,
                )
                instructor = Instructor.objects.create(
                    user=instructor_user, account_type="INSTRUCTOR"
                )
                instructor.save()
                return instructor
        except Exception as e:
            print("ERROR: creating instructor obj", row)
            print(e)
            self.bad_rows.append(str(self.rowNum) + " instructor")
            return None

    def create_course(self, row, instructor):
        try:
            name = row[1]
            course_id = row[2]
            category = row[4]
            tuition = float(row[5])
            room = row[6]
            start_date = arrow.get(row[7], "MM/DD/YYYY").format("YYYY-MM-DD")
            end_date = arrow.get(row[8], "MM/DD/YYYY").format("YYYY-MM-DD")
            day_of_week = row[9]
            start_time = row[10]
            end_time = row[11]
            max_capacity = row[12]
            note = row[13]

            with transaction.atomic():
                queryset = CourseCategory.objects.filter(name=category)
                if queryset.count() > 0:
                    course_category = queryset[0]
                else:
                    course_category = CourseCategory.objects.create(name=category)
                    course_category.save()

                course = Course.objects.create(
                    course_id=course_id,
                    subject=name,
                    instructor=instructor,
                    total_tuition=tuition,
                    room=room,
                    day_of_week=day_of_week,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time,
                    max_capacity=max_capacity,
                    course_type="class",
                    course_category=course_category,
                    is_confirmed=True,
                )
                course.save()
                print("created course")

                if isinstance(note, str):
                    course_note = CourseNote.objects.create(body=note, course=course)
                    course_note.save()
                return course
        except Exception as e:
            print("ERROR: creating course obj", row)
            print(e)
            self.bad_rows.append(str(self.rowNum) + " course")
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

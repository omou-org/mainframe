from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import pandas as pd

from account.models import Student
from course.models import Course, Enrollment, EnrollmentNote


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    bad_rows = []
    rowNum = 2

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully called'))
        dataframe = self.read_data_from_file("/Users/jerry/Desktop/omou/summit_tutoring_enrollment.csv")

        self.insert_accounts(dataframe)
        print(str(self.bad_rows))

    def read_data_from_file(self, file_name):
        return pd.read_csv(file_name)

    def insert_accounts(self, dataframe):
        for row in dataframe.itertuples():
            print(str(self.rowNum))

            self.create_enrollments(row)

            self.rowNum += 1

    def create_enrollments(self, row):
        try:
            course_id = row[2]
            student_id = row[4]

            if not isinstance(student_id, str):
                return None
            if not isinstance(student_id, str):
                return None

            course = Course.objects.get(course_id=course_id)
            student = Student.objects.get(user_uuid=int(student_id) + 55)

            # payment
            payment = row[5]

            # notes
            notes = row[6]

            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                payment=payment
            )
            enrollment.save()

            # enrollment note
            if isinstance(notes, str):
                enrollment_note = EnrollmentNote.objects.create(enrollment=enrollment, body=notes)
                enrollment_note.save()
        except Exception as e:
            print("ERROR: creating enrollment obj", row)
            print(e)

            self.bad_rows.append(str(self.rowNum))
            return None

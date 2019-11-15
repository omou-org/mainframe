from django.core.management.base import BaseCommand, CommandError
import pandas as pd

from course.models import Enrollment, EnrollmentNote


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    bad_rows = []
    rowNum = 2

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully called'))
        dataframe = self.read_data_from_file("/Users/jerry/Desktop/omou/summit_enrollment.csv")

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
            # course
            course_id = row[2]

            # student
            student_id = row[4]

            # payment
            payment = row[5]

            # notes
            notes = row[6]

            if not isinstance(student_id, float):
                enrollment = Enrollment.objects.create(student=student_id, course=course_id, payment=payment)
                enrollment.save()

                # enrollment note
                if not isinstance(notes, float):
                    enrollment_note = EnrollmentNote.objects.create(enrollment=enrollment, body=notes)
                    enrollment_note.save()
            else:
                print("missing student")
                self.bad_rows.append(str(self.rowNum) + " missing student")

        except Exception as e:
            print("ERROR: creating parent obj", row)
            print(e)

            self.bad_rows.append(str(self.rowNum))
            return None

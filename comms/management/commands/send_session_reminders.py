import arrow

from django.core.management.base import BaseCommand, CommandError

from comms.models import Email
from comms.templates import SESSION_REMINDER_TEMPLATE
from scheduler.models import Session


SESSION_REMINDER_PRIOR_HOURS = 8


class Command(BaseCommand):
    help = """
    Checks for upcoming sessions and send reminder emails to
    parents and instructors.
    """

    def handle(self, *args, **options):
        threshold = arrow.now().shift(hours=8).datetime
        sessions = Session.objects.filter(
            start_datetime__lte=threshold,
            sent_reminder=False
        )

        for session in sessions:
            # instructor reminder
            instructor_data = {
                "instructor_name": session.instructor.user.first_name,
                "sessions": [
                    {
                        "title": session.course.title,
                        "date": session.start_datetime.strftime("%m/%d/%Y"),
                        "start_time": session.start_datetime.strftime("%I:%M %p"),
                        "end_time": session.end_datetime.strftime("%I:%M %p")
                    }
                ]
            }
            email = Email(
                template_id=SESSION_REMINDER_TEMPLATE,
                recipient=session.instructor.user.email,
                data=instructor_data
            )
            email.save()
            session.sent_reminder = True
            session.save()
            print(session.__dict__)

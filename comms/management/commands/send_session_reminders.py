import arrow

from django.core.management.base import BaseCommand, CommandError

from comms.models import Email, InstructorNotificationSettings, ParentNotificationSettings
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
            start_datetime__gt=arrow.now().datetime,
            sent_upcoming_reminder=False
        )

        for session in sessions:
            email_data = {
                'instructor_name': session.instructor.user.first_name,
                'sessions': [
                    {
                        'title': session.course.title,
                        'date': session.start_datetime.strftime('%m/%d/%Y'),
                        'start_time': session.start_datetime.strftime('%I:%M %p'),
                        'end_time': session.end_datetime.strftime('%I:%M %p')
                    }
                ]
            }

            # instructor reminder
            instructor_settings = InstructorNotificationSettings.objects.get(instructor=session.instructor)
            if instructor_settings.session_reminder_email:
                Email.objects.create(
                    template_id=SESSION_REMINDER_TEMPLATE,
                    recipient=session.instructor.user.email,
                    data=email_data
                )

            # parent reminders
            for enrollment in session.course.enrollment_set.all():
                primary_parent = enrollment.student.primary_parent
                parent_settings = ParentNotificationSettings.objects.get(parent=primary_parent)
                if parent_settings.session_reminder_email:
                    Email.objects.create(
                        template_id=SESSION_REMINDER_TEMPLATE,
                        recipient=primary_parent.user.email,
                        data=email_data
                    )

            session.sent_upcoming_reminder = True
            session.save()

import arrow
import logging
import datetime
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

from comms.models import Email, InstructorNotificationSettings, ParentNotificationSettings, SMSNotification
from comms.templates import SESSION_REMINDER_TEMPLATE
from scheduler.models import Session


MISSED_TEMPLATE = 'd-128e4bccf2ee49f0b6190d0cb76eb045'


def run():
    """Checks for upcoming sessions and send reminder emails to parents and instructors."""
    sessions = Session.objects.filter(
        start_datetime__gte=arrow.now().shift(hours=-8).datetime,
        start_datetime__lt=arrow.now().datetime,
        sent_missed_reminder=False
    )
    logging.info(sessions)
    for session in sessions:
        email_data = {
            "first_name": "Gina",
            "sessions": [
                {
                    "title": session.course.title,
                    "date": (session.start_datetime - datetime.timedelta(hours=7))
                        .strftime('%m/%d/%Y'),
                    "start_time": (session.start_datetime - datetime.timedelta(hours=7))
                        .strftime('%I:%M %p'),
                    "end_time": (session.end_datetime - datetime.timedelta(hours=7))
                        .strftime('%I:%M %p')
                },
            ]
        }

        # parent reminders
        for enrollment in session.course.enrollment_set.all():
            primary_parent = enrollment.student.primary_parent
            email_data['first_name'] = primary_parent.user.first_name
            parent_settings = ParentNotificationSettings.objects.get(
                parent=primary_parent)
            if parent_settings.session_reminder_email:
                Email.objects.create(
                    template_id=MISSED_TEMPLATE,
                    recipient=primary_parent.user.email,
                    data=email_data
                )
            if parent_settings.session_reminder_sms:
                primary_parent = enrollment.student.primary_parent
                SMSNotification.objects.create(
                    recipient=primary_parent.phone_number,
                    data='hello'
                )

        session.sent_upcoming_reminder = True
        session.save()

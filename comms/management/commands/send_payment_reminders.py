import arrow

from django.core.management.base import BaseCommand

from comms.models import Email, ParentNotificationSettings
from comms.templates import PAYMENT_REMINDER_TEMPLATE
from course.models import Course
from scheduler.models import Session


class Command(BaseCommand):
    help = """
    Checks for upcoming final 1:1 sessions and send reminder emails to parents.
    """

    def handle(self, *args, **options):
        threshold = arrow.now().shift(hours=24).datetime
        sessions = Session.objects.filter(
            start_datetime__lte=threshold,
            start_datetime__gt=arrow.now().datetime,
            sent_payment_reminder=False,
            course__course_type=Course.TUTORING
        )

        for session in sessions:
            for enrollment in session.course.enrollment_set:
                # must be last paid session
                if enrollment.sessions_left != 1:
                    continue
                parent = enrollment.student.primary_parent
                parent_settings = ParentNotificationSettings.objects.get(parent=parent)

                if parent_settings.payment_reminder_email:
                    Email.objects.create(
                        template_id=PAYMENT_REMINDER_TEMPLATE,
                        recipient=parent.user.email,
                        data={
                            'parent_name': parent.user.first_name,
                            'course_name': enrollment.course.title
                        }
                    )

            session.sent_payment_reminder = True
            session.save()

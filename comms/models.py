from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

from account.models import Parent, Instructor
from course.models import Course


sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class Announcement(models.Model):
    subject = models.TextField()
    body = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    poster = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Email(models.Model):
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    COURSE_CHOICES = (
        (STATUS_SENT, "Tutoring"),
        (STATUS_FAILED, "Small group"),
    )

    template_id = models.CharField(max_length=50)
    sender = models.EmailField(default="omoudev@gmail.com")
    recipient = models.EmailField()
    data = JSONField()
    status = models.CharField(max_length=10)
    response_body = models.CharField(max_length=1000)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        message = Mail(
            to_emails=self.recipient,
            from_email=self.sender,
        )
        message.template_id = self.template_id
        message.dynamic_template_data = self.data
        try:
            response = sg.send(message)
            self.response_body = response.body
            self.status = self.STATUS_SENT
        except Exception as e:
            self.status = self.STATUS_FAILED
        super().save(*args, **kwargs)


class SMSNotification(models.Model):
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    COURSE_CHOICES = (
        (STATUS_SENT, "Tutoring"),
        (STATUS_FAILED, "Small group"),
    )

    sender = models.CharField(default="+15865018299", max_length=15)
    recipient = models.CharField(max_length=15)
    body = models.CharField(max_length=1000)
    response_status = models.CharField(max_length=20, null=True)
    response_body = models.CharField(max_length=1000, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            message = twilio.messages.create(
                body=self.body,
                from_=self.sender,
                to=self.recipient,
            )
            self.response_status = message.status
            self.response_body = message.error_message
        except Exception as e:
            pass

        super().save(*args, **kwargs)


class ParentNotificationSettings(models.Model):
    parent = models.OneToOneField(Parent, on_delete=models.PROTECT, primary_key=True)
    session_reminder_email = models.BooleanField(default=True)
    session_reminder_sms = models.BooleanField(default=False)
    payment_reminder_email = models.BooleanField(default=True)
    payment_reminder_sms = models.BooleanField(default=False)
    schedule_updates_sms = models.BooleanField(default=False)
    missed_session_reminder_email = models.BooleanField(default=True)
    missed_session_reminder_sms = models.BooleanField(default=False)
    course_requests_sms = models.BooleanField(default=False)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InstructorNotificationSettings(models.Model):
    instructor = models.OneToOneField(
        Instructor, on_delete=models.PROTECT, primary_key=True
    )
    session_reminder_email = models.BooleanField(default=True)
    session_reminder_sms = models.BooleanField(default=False)
    schedule_updates_sms = models.BooleanField(default=False)
    course_requests_sms = models.BooleanField(default=False)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

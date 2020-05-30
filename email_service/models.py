from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


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
    response_status = models.CharField(max_length=10)
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
            self.response_status = response.status_code
            self.response_body = response.body
        except Exception as e:
            self.response_status = e.message

        super().save(*args, **kwargs)


class SMSNotification(models.Model):
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    COURSE_CHOICES = (
        (STATUS_SENT, "Tutoring"),
        (STATUS_FAILED, "Small group"),
    )

    sender = models.CharField(default="+12513024126", max_length=15)
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

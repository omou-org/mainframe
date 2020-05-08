from django.db import models


class Email(models.Model):
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    COURSE_CHOICES = (
        (STATUS_SENT, "Tutoring"),
        (STATUS_FAILED, "Small group"),
    )

    template_id = models.CharField(max_length=50)
    sender = models.EmailField()
    recipient = models.EmailField()
    data = models.CharField()
    status = models.CharField()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

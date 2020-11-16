from django.db import models
from django.contrib.auth import get_user_model

from account.models import Instructor
from course.models import Course, CourseAvailability

from scheduler.managers import SessionManager


class Session(models.Model):
    title = models.TextField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
    )
    availability = models.ForeignKey(
        CourseAvailability, 
        on_delete=models.PROTECT
    )
    details = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    sent_upcoming_reminder = models.BooleanField(default=False)
    sent_payment_reminder = models.BooleanField(default=False)

    objects = SessionManager()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SessionNote(models.Model):
    subject = models.TextField()
    body = models.TextField()
    session = models.ForeignKey(
        Session,
        on_delete=models.PROTECT
    )
    poster = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
    )    

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
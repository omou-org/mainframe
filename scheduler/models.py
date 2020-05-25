from dateutil.parser import parse

from django.db import models

from account.models import Instructor
from course.models import Course

from account.models import Student

from scheduler.managers import SessionManager

class Session(models.Model):
    title = models.TextField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
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

    objects = SessionManager()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

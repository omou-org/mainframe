from django.db import models

from course.models import Course


class Session(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
    )
    details = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

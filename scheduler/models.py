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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

from datetime import datetime
from dateutil.parser import parse

from django.db import models
from django.db.models import Q

from course.models import Course

class SessionManager(models.Manager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial       

        if query is not None:
            # filter by session start date / time
            try:
                query = parse(query)
                qs = qs.filter(Q(start_datetime__date = query) | Q(start_datetime__time = query)).distinct()
            except ValueError:
                pass

            # filter by course instructor, enrollments, title

        return qs


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

    objects = SessionManager()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

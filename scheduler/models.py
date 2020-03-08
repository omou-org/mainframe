from dateutil.parser import parse

from django.db import models
from django.db.models import Q

from account.models import Instructor
from course.models import Course

from account.models import Student


class SessionManager(models.Manager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial       

        if query is not None:
            try:
                # filter by session start date / time
                query = parse(query)
                qs = qs.filter(Q(start_datetime__date=query) | Q(start_datetime__time=query)).distinct()
            except ValueError:
                
                # filter by course instructor, enrollments, title
                course_qs = Course.objects.search(query)
                student_qs = set(Student.objects.search(query).values_list("user", flat=True))
                
                session_courseID = set(qs.values_list("course__id", flat=True))
                valid_courseID = []
                for course_id in session_courseID:
                    course = Course.objects.get(id=course_id)
                    if course in course_qs:
                        valid_courseID.append(course_id)
                    elif not student_qs.isdisjoint(course.enrollment_list):
                        valid_courseID.append(course_id)
                
                qs = qs.filter(course__id__in=valid_courseID)

        return qs


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

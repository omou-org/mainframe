from django.db import models
from django.db.models import Q
from account.models import Instructor, Student

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CourseManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(type__icontains=query) |
                        Q(subject__icontains=query) |
                        Q(description__icontains=query) |
                        Q(instructor__user__first_name__icontains=query) |
                        Q(instructor__user__last_name__icontains=query) |
                        Q(room__icontains=query) |
                        Q(days__icontains=query) |
                        Q(course_category__name__icontains=query) |
                        Q(course_category__description__icontains=query)
                        )
            try:
                query = int(query)
                or_lookup |= (Q(tuition=query))
            except ValueError:
                pass
            qs = qs.filter(or_lookup).distinct()
        return qs

class Course(models.Model):
    CLASS = 'C'
    TUTORING = 'T'
    TYPE_CHOICES = (
        (CLASS, 'Class'),
        (TUTORING, 'Tutoring'),
    )

    # Course information
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=CLASS,
    )
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT)
    tuition = models.DecimalField(max_digits=6, decimal_places=2)

    # Logistical information
    room = models.CharField(max_length=50)
    days = models.CharField(max_length=10)
    schedule = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    max_capacity = models.IntegerField()

    # One-to-many relationship with CourseCategory
    course_category = models.ForeignKey(
        CourseCategory, on_delete=models.PROTECT, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.db.models import Q
from account.models import Instructor, Student


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CourseManager(models.Manager):
    def search(self, qs_before, query=None):
        if qs_before is None:
            qs = self.get_queryset()
        qs = qs_before

        if query is not None:
            or_lookup = (Q(type__icontains=query) |
                Q(subject__icontains=query) |
                Q(description__icontains=query) |
                Q(instructor__user__first_name__icontains=query) |
                Q(instructor__user__last_name__icontains=query) |
                Q(room__icontains=query) |
                Q(day_of_week__icontains=query) |
                Q(course_category__name__icontains=query) |
                Q(course_category__description__icontains=query))
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
    course_id = models.CharField(max_length=50, primary_key=True)
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT, null=True, blank=True)
    tuition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Logistical information
    room = models.CharField(max_length=50, null=True, blank=True)
    day_of_week = models.CharField(max_length=27)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.IntegerField(null=True, blank=True)

    # One-to-many relationship with CourseCategory
    course_category = models.ForeignKey(
        CourseCategory, on_delete=models.PROTECT, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    @property
    def enrollment_list(self):
        return [enrollment.student.user.id for enrollment in self.enrollment_set.all()]

    @property
    def enrollment_id_list(self):
        return [enrollment.id for enrollment in self.enrollment_set.all()]


class CourseNote(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)    
    title = models.TextField(blank=True)
    body = models.TextField()
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT
    )
    important = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    payment = models.CharField(max_length=15, null=True, blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EnrollmentNote(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)    
    title = models.TextField(blank=True)
    body = models.TextField()
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT
    )
    important = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

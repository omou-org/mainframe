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
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

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
                or_lookup |= (Q(hourly_tuition=query))
            except ValueError:
                pass
            qs = qs.filter(or_lookup).distinct()
        return qs


class Course(models.Model):
    TUTORING = "T"
    SMALL_GROUP = "S"
    CLASS = "C"
    COURSE_CHOICES = (
        (TUTORING, "Tutoring"),
        (SMALL_GROUP, "Small group"),
        (CLASS, "Class"),
    )

    ELEMENTARY_LEVEL = 'E'
    MIDDLE_LEVEL = 'M'
    HIGH_LEVEL = 'H'
    COLLEGE_LEVEL = 'C'
    ACADEMIC_LEVEL_CHOICES = (
        (ELEMENTARY_LEVEL, 'Elementary School Level'),
        (MIDDLE_LEVEL, 'Middle School Level'),
        (HIGH_LEVEL, 'High School Level'),
        (COLLEGE_LEVEL, 'College Level'),
    )

    # Course information
    course_type = models.CharField(
        max_length=1,
        choices=COURSE_CHOICES,
        default=CLASS,
    )
    academic_level = models.CharField(
        max_length=15,
        choices=ACADEMIC_LEVEL_CHOICES,
        null=True,
        blank=True,
    )

    course_id = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT, null=True, blank=True)
    hourly_tuition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_tuition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Logistical information
    room = models.CharField(max_length=50, null=True, blank=True)
    day_of_week = models.CharField(max_length=27)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    num_sessions = models.IntegerField(default=0)
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

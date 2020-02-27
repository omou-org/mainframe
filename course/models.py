from datetime import date, datetime, timezone
from decimal import Decimal
from math import floor

from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
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
            or_lookup = (Q(course_type__icontains=query) |
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
    TUTORING = "tutoring"
    SMALL_GROUP = "small_group"
    CLASS = "class"
    COURSE_CHOICES = (
        (TUTORING, "Tutoring"),
        (SMALL_GROUP, "Small group"),
        (CLASS, "Class"),
    )

    ELEMENTARY_LVL = "elementary_lvl"
    MIDDLE_LVL = "middle_lvl"
    HIGH_LVL = "high_lvl"
    COLLEGE_LVL = "college_lvl"
    ACADEMIC_CHOICES = (
        (ELEMENTARY_LVL, "Elementary"),
        (MIDDLE_LVL, "Middle"),
        (HIGH_LVL, "High"),
        (COLLEGE_LVL, "College"),
    )
    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    # Course information
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_CHOICES,
        default=TUTORING
    )
    academic_level = models.CharField(
        max_length=20,
        choices=ACADEMIC_CHOICES,
        default=ELEMENTARY_LVL
    )
    course_id = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT, null=True, blank=True)
    hourly_tuition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_tuition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Logistical information
    room = models.CharField(max_length=50, null=True, blank=True)
    day_of_week = models.CharField(max_length=9, choices=DAYS_OF_WEEK, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    num_sessions = models.IntegerField(default=0)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.IntegerField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    # One-to-many relationship with CourseCategory
    course_category = models.ForeignKey(
        CourseCategory, on_delete=models.PROTECT, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    @property
    def session_length(self):
        duration_sec = (datetime.combine(date.min, self.end_time) -
                        datetime.combine(date.min, self.start_time)).seconds
        duration_hours = Decimal(duration_sec) / (60 * 60)
        return duration_hours

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

    @cached_property
    def enrollment_balance(self):
        balance = 0
        for registration in self.registration_set.all():
            balance += (registration.num_sessions * self.course.hourly_tuition *
                        self.course.session_length)

        earliest_attendance = self.registration_set.earliest(
            'attendance_start_date').attendance_start_date
        past_sessions = self.course.session_set.filter(
            start_datetime__gte=earliest_attendance,
            start_datetime__lte=datetime.now(timezone.utc),
        )
        for session in past_sessions:
            session_length_sec = (session.end_datetime - session.start_datetime).seconds
            session_length_hours = Decimal(session_length_sec) / (60 * 60)
            balance -= Decimal(session_length_hours) * self.course.hourly_tuition

        return balance

    @property
    def sessions_left(self):
        return floor(self.enrollment_balance /
                     (self.course.session_length * self.course.hourly_tuition))

    @property
    def last_paid_session_datetime(self):
        if self.sessions_left <= 0:
            past_sessions = self.course.session_set.filter(
                start_datetime__lte=datetime.now(timezone.utc)
            ).order_by('-start_datetime')
            if abs(self.sessions_left) >= len(past_sessions):
                return None
            return past_sessions[abs(self.sessions_left)].start_datetime

        future_sessions = self.course.session_set.filter(
            start_datetime__gt=datetime.now(timezone.utc)
        ).order_by('start_datetime')
        last_index = min(self.sessions_left, len(future_sessions)) - 1
        return future_sessions[last_index].start_datetime

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

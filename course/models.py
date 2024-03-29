from datetime import datetime, timezone
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

from account.models import Instructor, Parent, Student
from onboarding.models import Business

from course.managers import CourseManager, EnrollmentManager


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def active_tuition_rule_count(self):
        return self.tuitionrule_set.filter(retired=False).count()


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

    # Course information
    course_type = models.CharField(
        max_length=20, choices=COURSE_CHOICES, default=TUTORING
    )
    academic_level = models.CharField(
        max_length=20, choices=ACADEMIC_CHOICES, default=ELEMENTARY_LVL
    )
    course_id = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.PROTECT, null=True, blank=True
    )
    hourly_tuition = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    total_tuition = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    business = models.ForeignKey(Business, on_delete=models.PROTECT, null=True)
    course_link = models.URLField(max_length=128, db_index=True, null=True, blank=True)
    course_link_description = models.CharField(max_length=1000, null=True, blank=True)
    course_link_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True
    )
    course_link_updated_at = models.DateTimeField(null=True, blank=True)

    # GAPI
    google_class_code = models.CharField(max_length=7, null=True, blank=True)

    # Logistical information
    room = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    num_sessions = models.IntegerField(default=0)
    max_capacity = models.IntegerField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    enrollment_deadline = models.DateField(null=True, blank=True)

    # One-to-many relationship with CourseCategory
    course_category = models.ForeignKey(
        CourseCategory, on_delete=models.PROTECT, null=True
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    @property
    def is_full(self):
        return self.max_capacity == Enrollment.objects.filter(course=self.id).count()

    @property
    def active_availability_list(self):
        return CourseAvailability.objects.filter(Q(course=self.id) & Q(active=True))

    @property
    def availability_list(self):
        return CourseAvailability.objects.filter(course=self.id)

    @property
    def enrollment_list(self):
        return [enrollment.student.user.id for enrollment in self.enrollment_set.all()]

    @property
    def enrollment_id_list(self):
        return [enrollment.id for enrollment in self.enrollment_set.all()]


class CourseAvailability(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    num_sessions = models.IntegerField(default=0)

    DAYS_OF_WEEK = (
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    )
    day_of_week = models.CharField(
        max_length=9, choices=DAYS_OF_WEEK, null=True, blank=True
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    active = models.BooleanField(default=True)


class CourseNote(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.TextField(blank=True)
    body = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    important = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)


class Enrollment(models.Model):
    SENT = "sent"
    UNSENT = "unsent"
    ACCEPTED = "accepted"
    INVALID_EMAIL = "invalid_email"
    STATUS_CHOICES = (
        (SENT, "Sent"),
        (UNSENT, "Unsent"),
        (ACCEPTED, "Accepted"),
        (INVALID_EMAIL, "Invalid_Email"),
    )

    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    invite_status = models.CharField(
        max_length=13,
        choices=STATUS_CHOICES,
        default=UNSENT,
    )

    @cached_property
    def enrollment_balance(self):
        earliest_attendance = self.registration_set.earliest(
            "attendance_start_date"
        ).attendance_start_date
        past_sessions = self.course.session_set.filter(
            start_datetime__gte=earliest_attendance,
            start_datetime__lte=datetime.now(timezone.utc),
        )

        total_balance = 0
        paid_balance = 0
        total_paid_sessions = sum(
            registration.num_sessions
            for registration in self.registration_set.all()
            if registration.invoice.payment_status == "paid"
        )

        for session in past_sessions:
            session_length_sec = (session.end_datetime - session.start_datetime).seconds
            session_length_hours = Decimal(session_length_sec) / (60 * 60)
            session_balance = Decimal(session_length_hours) * self.course.hourly_tuition

            if total_paid_sessions > 0:
                paid_balance += session_balance
            total_balance += session_balance

            total_paid_sessions -= 1

        return Decimal(total_balance - paid_balance)

    @property
    def sessions_left(self):
        total_paid_sessions = sum(
            registration.num_sessions
            for registration in self.registration_set.all()
            if registration.invoice.payment_status == "paid"
        )
        return self.course.num_sessions - total_paid_sessions

    @property
    def last_paid_session_datetime(self):
        if self.sessions_left <= 0:
            past_sessions = self.course.session_set.filter(
                start_datetime__lte=datetime.now(timezone.utc)
            ).order_by("-start_datetime")
            if abs(self.sessions_left) >= len(past_sessions):
                return None
            return past_sessions[abs(self.sessions_left)].start_datetime

        future_sessions = self.course.session_set.filter(
            start_datetime__gt=datetime.now(timezone.utc)
        ).order_by("start_datetime")
        last_index = min(self.sessions_left, len(future_sessions)) - 1
        return future_sessions[last_index].start_datetime

    @property
    def enrollment_status(self):
        invoices = self.registration_set.values_list("invoice", flat=True)
        if invoices:
            return invoices.order_by("-created_at")[0].payment_status

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentManager()


def create_enrollment_attendances(instance, created, raw, **kwargs):
    from scheduler.models import Attendance

    if not created or raw:
        return

    if instance.course and instance.attendance_set.count() == 0:
        for session in instance.course.session_set.all():
            Attendance.objects.create(
                enrollment=instance,
                session=session,
            )


models.signals.post_save.connect(
    create_enrollment_attendances,
    sender=Enrollment,
    dispatch_uid="create_enrollment_attendances",
)


class EnrollmentNote(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.TextField(blank=True)
    body = models.TextField()
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT)
    important = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)


class Interest(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

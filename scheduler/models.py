from django.db import models
from django.contrib.auth import get_user_model

from account.models import Instructor, Student
from course.models import Course, CourseAvailability, CourseCategory, Enrollment
from scheduler.managers import SessionManager


class Session(models.Model):
    title = models.TextField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
    )
    availability = models.ForeignKey(CourseAvailability, on_delete=models.PROTECT)
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
    sent_upcoming_reminder = models.BooleanField(default=False)
    sent_payment_reminder = models.BooleanField(default=False)
    sent_missed_reminder = models.BooleanField(default=False)

    objects = SessionManager()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


def create_session_attendances(instance, created, raw, **kwargs):
    if not created or raw:
        return

    if instance.course and instance.attendance_set.count() == 0:
        for enrollment in instance.course.enrollment_set.all():
            Attendance.objects.create(
                enrollment=enrollment,
                session=instance,
            )


models.signals.post_save.connect(
    create_session_attendances,
    sender=Session,
    dispatch_uid="create_session_attendances",
)


class SessionNote(models.Model):
    subject = models.TextField()
    body = models.TextField()
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    poster = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Attendance(models.Model):
    PRESENT = "present"
    TARDY = "tardy"
    ABSENT = "absent"
    UNSET = "unset"
    STATUS_CHOICES = (
        (UNSET, "Unset"),
        (PRESENT, "Present"),
        (TARDY, "Tardy"),
        (ABSENT, "Absent"),
    )

    status = models.CharField(
        max_length=7,
        choices=STATUS_CHOICES,
        default=UNSET,
    )

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TutoringRequest(models.Model):
    DAYS_OF_WEEK = (
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    )

    SUBMITTED = "submitted"
    PENDING_INSTRUCTOR_APPROVAL = "pending_instructor_approval"
    PENDING_ADMIN_APPROVAL = "pending_admin_approval"
    REQUEST_STATUS = (
        (SUBMITTED, "Submitted"),
        (PENDING_INSTRUCTOR_APPROVAL, "Pending Instructor Approval"),
        (PENDING_ADMIN_APPROVAL, "Pending Admin Approval"),
    )

    MANUAL = "manual"
    SUBSCRIPTION = "subscription"
    INVOICE_SETTING = (
        (MANUAL, "Manual"),
        (SUBSCRIPTION, "Subscription"),
    )

    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    instructor = models.ForeignKey(Instructor, null=True, on_delete=models.PROTECT)
    course_topic = models.ForeignKey(CourseCategory, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    duration = models.IntegerField()  # duration in minutes
    request_status = models.CharField(max_length=50, choices=REQUEST_STATUS)
    invoice_setting = models.CharField(max_length=20, choices=INVOICE_SETTING)

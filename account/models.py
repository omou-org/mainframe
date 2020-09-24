from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_localflavor_us.us_states import US_STATES
from django.conf import settings

from account.managers import StudentManager, ParentManager, InstructorManager, AdminManager


class UserInfo(models.Model):
    # Account type
    STUDENT_TYPE = 'student'
    PARENT_TYPE = 'parent'
    INSTRUCTOR_TYPE = 'instructor'
    ADMIN_TYPE = 'admin'
    ACCOUNT_TYPE_CHOICES = (
        (STUDENT_TYPE, 'Student'),
        (PARENT_TYPE, 'Parent'),
        (INSTRUCTOR_TYPE, 'Instructor'),
        (ADMIN_TYPE, 'Admin'),
    )

    # Gender
    MALE_GENDER = 'male'
    FEMALE_GENDER = 'female'
    UNSPECIFIED_GENDER = 'unspecified'
    GENDER_CHOICES = (
        (MALE_GENDER, 'Male'),
        (FEMALE_GENDER, 'Female'),
        (UNSPECIFIED_GENDER, 'Unspecified'),
    )
    STATE_CHOICES = tuple(sorted(US_STATES, key=lambda obj: obj[1]))

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.PROTECT,
        primary_key=True,
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    user_uuid = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default=UNSPECIFIED_GENDER,
    )
    birth_date = models.DateField(blank=True, null=True)

    # Address
    address = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=32, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=16, choices=STATE_CHOICES, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    class Meta:
        abstract = True



class Note(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.TextField(blank=True)
    body = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    important = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class School(models.Model):
    name = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    district = models.CharField(max_length=100, blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Student(UserInfo):
    # 0 is preschool/kindergarten, 13 is graduated
    grade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(13)],
        null=True,
        blank=True,
    )
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    primary_parent = models.ForeignKey(
        "Parent",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="student_primary_parent",
    )

    secondary_parent = models.ForeignKey(
        "Parent",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="student_secondary_parent",
    )

    objects = StudentManager()

    @property
    def enrollment_id_list(self):
        return [enrollment.id for enrollment in self.enrollment_set.all()]

class StudentSchoolInfo(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT
    )
    textbook = models.CharField(max_length=512)
    teacher = models.CharField(max_length=100)
    current_grade = models.CharField(max_length=5)
    current_topic = models.CharField(max_length=64)
    student_strengths=models.CharField(max_length=1024)
    student_weaknesses=models.CharField(max_length=1024)
    
class Parent(UserInfo):
    MOTHER_REL = "mother"
    FATHER_REL = "father"
    GUARDIAN_REL = "guardian"
    OTHER_REL = "other"

    RELATIONSHIP_CHOICES = (
        (MOTHER_REL, "Mother"),
        (FATHER_REL, "Father"),
        (GUARDIAN_REL, "Guardian"),
        (OTHER_REL, "Other"),
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        null=True,
    )
    balance = models.DecimalField(decimal_places=2, default=0.0, max_digits=6)
    secondary_phone_number = models.CharField(max_length=50, blank=True, null=True)
    objects = ParentManager()

    @property
    def student_list(self):
        return [student.user.id for student in self.student_primary_parent.all().union(
            self.student_secondary_parent.all())]


class Instructor(UserInfo):
    objects = InstructorManager()

    biography = models.CharField(max_length=2000, null=True, blank=True)
    experience = models.CharField(max_length=2000, null=True, blank=True)
    language = models.CharField(max_length=2000, null=True, blank=True)
    subjects = models.ManyToManyField('course.CourseCategory', blank=True)


class InstructorAvailability(models.Model):
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
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

    day_of_week = models.CharField(max_length=9, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InstructorOutOfOffice(models.Model):
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Admin(UserInfo):
    OWNER_TYPE = "owner"
    RECEPTIONIST_TYPE = "receptionist"
    ASSISTANT_TYPE = "assistant"

    TYPE_CHOICES = (
        (OWNER_TYPE, "Owner"),
        (RECEPTIONIST_TYPE, "Receptionist"),
        (ASSISTANT_TYPE, "Assistant"),
    )
    admin_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    objects = AdminManager()

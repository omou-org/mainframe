from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_localflavor_us.us_states import US_STATES
from django.conf import settings

class UserInfo(models.Model):
    # Gender
    MALE_GENDER = 'M'
    FEMALE_GENDER = 'F'
    UNSPECIFIED_GENDER = 'U'
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
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=UNSPECIFIED_GENDER,
    )
    birth_date = models.DateField()

    # Address
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=15)
    state = models.CharField(max_length=16, choices=STATE_CHOICES)
    zipcode = models.CharField(max_length=10)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

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


class Student(UserInfo):
    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    # 0 is preschool/kindergarten, 13 is graduated
    grade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(13)],
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    school = models.CharField(max_length=64)

    parent = models.ForeignKey(
        "Parent",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )


class Parent(UserInfo):
    MOTHER_REL = "MOTHER"
    FATHER_REL = "FATHER"
    GUARDIAN_REL = "GUARDIAN"
    OTHER_REL = "OTHER"

    RELATIONSHIP_CHOICES = (
        (MOTHER_REL, "Mother"),
        (FATHER_REL, "Father"),
        (GUARDIAN_REL, "Guardian"),
        (OTHER_REL, "Other"),
    )
    relationship = models.CharField(
        max_length=10,
        choices=RELATIONSHIP_CHOICES,
    )


class Instructor(UserInfo):
    age = models.IntegerField()


class Admin(UserInfo):
    OWNER_TYPE = "OWNER"
    RECEPTIONIST_TYPE = "RECEPTIONIST"
    ASSISSTANT_TYPE = "ASSISSTANT"

    TYPE_CHOICES = (
        (OWNER_TYPE, "Owner"),
        (RECEPTIONIST_TYPE, "Receptionist"),
        (ASSISSTANT_TYPE, "Assisstant"),
    )
    admin_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

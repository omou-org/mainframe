from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_localflavor_us.us_states import US_STATES


class UserInfo(models.Model):
    # Gender
    MALE = 'M'
    FEMALE = 'F'
    UNSPECIFIED = 'U'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNSPECIFIED, 'Unspecified'),
    )
    STATE_CHOICES = tuple(sorted(US_STATES, key=lambda obj: obj[1]))

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=UNSPECIFIED,
    )

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


class Student(UserInfo):
    # 0 is preschool/kindergarten, 13 is graduated
    grade = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(13)],
    )
    age = models.IntegerField()
    school = models.CharField(max_length=64)


class Instructor(UserInfo):
    age = models.IntegerField()

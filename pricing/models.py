from django.db import models
from course.models import CourseCategory
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class PriceRule(models.Model):
    # Basic price information
    name = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    hourly_tuition = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        default=-1,
    )
    
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

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    # Basic discount information
    
    name = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    description = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    PERCENT = "percent"
    FIXED = "fixed"

    AMOUNT_CHOICES = (
        (PERCENT, "percent"),
        (FIXED, "fixed")
    )
    amount_type = models.CharField(
        max_length=10,
        choices=AMOUNT_CHOICES,
        default=FIXED
    )

    active = models.BooleanField(default=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MultiCourseDiscount(Discount):
    discount = Discount()

    num_sessions = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(1000)],
    )


class DateRangeDiscount(Discount):
    discount = Discount()

    start_date = models.DateField()
    end_date = models.DateField()


class PaymentMethodDiscount(Discount):
    discount = Discount()

    payment_method = models.CharField(max_length=50)
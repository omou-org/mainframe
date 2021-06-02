from django.db import models
from account.models import Business
from course.models import CourseCategory
from django.core.validators import MaxValueValidator, MinValueValidator
from pricing.managers import TuitionRuleManager

# Create your models here.


class TuitionRule(models.Model):
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
    ELEMENTARY_LVL = "elementary_lvl"
    MIDDLE_LVL = "middle_lvl"
    HIGH_LVL = "high_lvl"
    COLLEGE_LVL = "college_lvl"

    TUTORING = "tutoring"
    SMALL_GROUP = "small_group"
    CLASS = "class"
    COURSE_CHOICES = (
        (TUTORING, "Tutoring"),
        (SMALL_GROUP, "Small group"),
        (CLASS, "Class"),
    )
    course_type = models.CharField(
        max_length=20, choices=COURSE_CHOICES, default=TUTORING
    )

    all_instructors_apply = models.BooleanField(default=True)
    instructors = models.ManyToManyField("account.Instructor", blank=True)

    business = models.ForeignKey(Business, on_delete=models.PROTECT, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TuitionRuleManager()


class Discount(models.Model):
    # Basic discount information
    name = models.CharField(
        max_length=1000,
        blank=True,
    )
    description = models.CharField(
        max_length=1000,
        blank=True,
    )
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    PERCENT = "percent"
    FIXED = "fixed"

    AMOUNT_CHOICES = (
        (PERCENT, "percent"),
        (FIXED, "fixed"),
    )
    amount_type = models.CharField(
        max_length=10,
        choices=AMOUNT_CHOICES,
        default=FIXED,
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

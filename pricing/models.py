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

    instructors = models.ManyToManyField("account.Instructor", blank=True)
    retired = models.BooleanField(default=False)

    business = models.ForeignKey(Business, on_delete=models.PROTECT, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TuitionRuleManager()

    @property
    def tuition_price_list(self):
        return [
            tuition_price
            for tuition_price in self.tuitionprice_set.order_by("-created_at")
        ]


class TuitionPrice(models.Model):
    tuition_rule = models.ForeignKey(TuitionRule, on_delete=models.PROTECT, default=-1)
    all_instructors_apply = models.BooleanField(default=True)
    hourly_tuition = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    # Basic discount information
    code = models.CharField(
        max_length=1000,
        blank=True,
    )
    auto_apply = models.BooleanField(default=False)

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
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    active = models.BooleanField(default=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    min_courses = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(1000)],
        blank=True,
        null=True,
    )

    CASH = "cash"
    CREDIT_CARD = "credit_card"
    COURSE_CREDIT = "course_credit"
    CHECK = "check"
    INTL_CREDIT_CARD = "intl_credit_card"
    METHOD_CHOICES = (
        (CASH, "Cash"),
        (COURSE_CREDIT, "Course Credit"),
        (CREDIT_CARD, "Credit Card"),
        (CHECK, "Check"),
        (INTL_CREDIT_CARD, "International Credit Card"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        null=True,
        blank=True,
    )

    all_courses_apply = models.BooleanField(default=True)
    courses = models.ManyToManyField("course.course", blank=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class MultiCourseDiscount(Discount):
#     discount = Discount()

#     num_sessions = models.IntegerField(
#         validators=[MinValueValidator(2), MaxValueValidator(1000)],
#     )


# class DateRangeDiscount(Discount):
#     discount = Discount()

#     start_date = models.DateField()
#     end_date = models.DateField()


# class PaymentMethodDiscount(Discount):
#     discount = Discount()

#     payment_method = models.CharField(max_length=50)

from django.db import models
from course.models import CourseCategory

# Create your models here.


class PriceRule(models.Model):
    # Basic price information
    name = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    hourly_tuition = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        default=-1,
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
    academic_level = models.CharField(
        max_length=20,
        choices=ACADEMIC_CHOICES,
        default=ELEMENTARY_LVL
    )
    TUTORING = "tutoring"
    SMALL_GROUP = "small_group"
    CLASS = "class"
    COURSE_CHOICES = (
        (TUTORING, "Tutoring"),
        (SMALL_GROUP, "Small group"),
        (CLASS, "Class"),
    )
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_CHOICES,
        default=TUTORING
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

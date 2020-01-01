from django.db import models

from account.models import Parent
from course.models import Enrollment


class Payment(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.PROTECT)
    base_amount = models.DecimalField(max_digits=6, decimal_places=2)
    # applied_discounts = models.ManyToManyField("DiscountRule")
    price_adjustment = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
    )
    total_amount = models.DecimalField(max_digits=6, decimal_places=2)

    CASH = 'cash'
    CREDIT_CARD = 'credit_card'
    COURSE_CREDIT = 'course_credit'
    METHOD_CHOICES = (
        (CASH, 'Cash'),
        (COURSE_CREDIT, 'Course Credit'),
        (CREDIT_CARD, 'Credit Card'),
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
    )
    enrollments = models.ManyToManyField(Enrollment, through='Registration')

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Registration associates a Payment with an Enrollment
class Registration(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    num_sessions = models.IntegerField()

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
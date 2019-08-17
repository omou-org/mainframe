from django.db import models
from django.core.validators import MinValueValidator

from course.models import Course, Session
from account.models import Student

from decimal import *


class Payment(models.Model):
    CASH = 'CASH'
    CARD = 'CARD'
    CHECK = 'CHECK'
    PAYMENT_METHOD_CHOICES = (
        (CASH, 'Cash'),
        (CARD, 'Card'),
        (CHECK, 'Check'),
    )

    method = models.CharField(
        max_length=5,
        choices=PAYMENT_METHOD_CHOICES,
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    description = models.CharField(max_length=1000)
    date_time = models.DateTimeField(auto_now=True)

    # Many-to-one relationship with Student
    student = models.ForeignKey(Student, on_delete=models.PROTECT)

    # Many-to-one relationship with Course
    course = models.ForeignKey(Course, on_delete=models.PROTECT)


class SessionPayment(models.Model):
    PAID = 'PAID'
    WAIVED = 'WAIVED'
    STATUS_CHOICES = (
        (PAID, 'Paid'),
        (WAIVED, 'Waived'),
    )

    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal(0.0))])
    date_time = models.DateTimeField(auto_now=True)

    # Many-to-one relationship with Student
    student = models.ForeignKey(Student, on_delete=models.PROTECT)

    # Many-to-one relationship with Session
    session = models.ForeignKey(Session, on_delete=models.PROTECT)

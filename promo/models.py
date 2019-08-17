from django.db import models
from django.core.validators import MinValueValidator

from course.models import Session

from decimal import *


class Promo(models.Model):
    AMOUNT = 'AMOUNT'
    PERCENTAGE = 'PERCENTAGE'
    DISCOUNT_TYPE_CHOICES = (
        (AMOUNT, 'Amount'),
        (PERCENTAGE, 'Percentage'),
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
    )
    discount = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal(0.0))])
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    # Many-to-many relationship with Session
    sessions = models.ManyToManyField(Session)

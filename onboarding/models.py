from django.db import models


class Business(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(max_length=200)
    address = models.CharField(max_length=200)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def availability_list(self):
        return BusinessAvailability.objects.filter(business=self.id)


class BusinessAvailability(models.Model):
    business = models.ForeignKey(Business, on_delete=models.PROTECT)
    DAYS_OF_WEEK = (
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    )
    day_of_week = models.CharField(
        max_length=9, choices=DAYS_OF_WEEK, null=True, blank=True
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

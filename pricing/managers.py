from django.db import models
from django.db.models import Q


class TuitionRuleManager(models.Manager):
    def business(self, business_id):
        qs = self.get_queryset()
        if business_id is not None:
            qs = qs.filter(business=business_id)
        return qs
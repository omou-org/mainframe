from django.db import models
from django.db.models import Q


class AccountManager(models.Manager):
    def business(self, business_id):
        qs = self.get_queryset()
        if business_id is not None:
            qs = qs.filter(business=business_id)
        return qs


class StudentManager(AccountManager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

        if query is not None:
            or_lookup = (Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__iexact=query) |
                Q(user_uuid__iexact=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(state__icontains=query) |
                Q(zipcode__icontains=query) |
                Q(school__name__icontains=query) |
                Q(primary_parent__user__first_name__icontains=query) |
                Q(primary_parent__user__last_name__icontains=query) |
                Q(secondary_parent__user__first_name__icontains=query) |
                Q(secondary_parent__user__last_name__icontains=query))
            try:
                query = int(query)
                or_lookup |= Q(grade=query)
            except ValueError:
                pass
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class ParentManager(AccountManager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

        if query is not None:
            or_lookup = (Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(state__icontains=query) |
                Q(zipcode__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs


class InstructorManager(AccountManager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

        if query is not None:
            or_lookup = (Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(state__icontains=query) |
                Q(zipcode__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs


class AdminManager(AccountManager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

        if query is not None:
            or_lookup = (Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(state__icontains=query) |
                Q(zipcode__icontains=query) |
                Q(admin_type__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs
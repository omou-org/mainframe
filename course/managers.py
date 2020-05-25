from django.db import models
from django.db.models import Q

class CourseManager(models.Manager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial

        if query is not None:
            or_lookup = (Q(course_type__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(instructor__user__first_name__icontains=query) |
                Q(instructor__user__last_name__icontains=query) |
                Q(room__icontains=query) |
                Q(day_of_week__icontains=query) |
                Q(course_category__name__icontains=query) |
                Q(course_category__description__icontains=query))
            try:
                query = int(query)
                or_lookup |= (Q(hourly_tuition=query))
            except ValueError:
                pass
            qs = qs.filter(or_lookup).distinct()
        return qs
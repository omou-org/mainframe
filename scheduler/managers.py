from django.db import models
from dateutil.parser import parse
from account.models import Student
from course.models import Course
from django.db.models import Q


class SessionManager(models.Manager):
    def search(self, query=None, qs_initial=None):
        if qs_initial is None or len(qs_initial) == 0:
            qs = self.get_queryset()
        else:
            qs = qs_initial       

        if query is not None:
            try:
                # filter by session start date / time
                query = parse(query)
                qs = qs.filter(Q(start_datetime__date=query) | Q(start_datetime__time=query)).distinct()
            except ValueError:
                
                # filter by course instructor, enrollments, title
                course_qs = Course.objects.search(query)
                student_qs = set(Student.objects.search(query).values_list("user", flat=True))
                
                session_courseID = set(qs.values_list("course__id", flat=True))
                valid_courseID = []
                for course_id in session_courseID:
                    course = Course.objects.get(id=course_id)
                    if course in course_qs:
                        valid_courseID.append(course_id)
                    elif not student_qs.isdisjoint(course.enrollment_list):
                        valid_courseID.append(course_id)
                
                qs = qs.filter(course__id__in=valid_courseID)

        return qs

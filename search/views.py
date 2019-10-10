from itertools import chain
from rest_framework import generics
from rest_framework.response import Response

from account.models import (
    Admin,
    Student,
    Parent,
    Instructor
)

from course.models import (
    Course,
)

from scheduler.models import (
    Session,
)

from search.serializers import SearchViewSerializer

class SearchView(generics.ListAPIView):    
    serializer_class = SearchViewSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        if query:
            queryset_chain = chain(
                Student.objects.search(query),
                Parent.objects.search(query),
                Instructor.objects.search(query),
                Course.objects.search(query))
            return list(queryset_chain)
        return list(Student.objects.none())

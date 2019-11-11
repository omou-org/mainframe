from itertools import chain
from rest_framework import generics
from rest_framework.response import Response

from account.models import (
    Student,
    Parent,
    Instructor
)

from course.models import (
    Course,
    Enrollment
)

from search.serializers import SearchViewSerializer

class AccountsSearchView(generics.ListAPIView): 
    serializer_class = SearchViewSerializer

    def get_queryset(self):
        searchResults = Student.objects.none()

        # query input check
        query = self.request.query_params.get('query', None)
        if (query is None or not query.isalnum()):
            return list(searchResults) 

        # query with profile filter
        profileFilter = self.request.query_params.get('profileFilter', None)
        if (profileFilter is not None):
            if (profileFilter == "Student"):
                searchResults = Student.objects.search(query);

                gradeFilter = self.request.query_params.get('gradeFilter', None)
                if (gradeFilter is not None):
                    try:
                        gradeFilter = int(gradeFilter)
                        if 1 <= gradeFilter and gradeFilter <= 12:
                            searchResults = searchResults.filter(grade=gradeFilter)
                    except ValueError:
                        pass
            elif (profileFilter == "Instructor"):
                searchResults = Instructor.objects.search(query)
            elif (profileFilter == "Admin"):
                searchResults = Admin.objects.search(query)
        # query on all models
        else:
            searchResults = chain(
                Student.objects.search(query),
                Parent.objects.search(query),
                Instructor.objects.search(query))

        # sort results
        sortFilter = self.request.query_params.get('sort', None)
        if (sortFilter is not None):
            if (sortFilter == "alphaAsc"):
                searchResults = sorted(searchResults, key=lambda obj:obj.user.first_name)
            elif (sortFilter == "alphaDesc"):
                searchResults = sorted(searchResults, key=lambda obj:obj.user.first_name, reverse=True)
            elif (sortFilter == "idAsc"):
                searchResults = sorted(searchResults, key=lambda obj:obj.user.id)
            elif (sortFilter == "idDesc"): 
                searchResults = sorted(searchResults, key=lambda obj:obj.user.id, reverse=True)
        return list(searchResults)

class CoursesSearchView(generics.ListAPIView):
    serializer_class = SearchViewSerializer

    def get_queryset(self):
        searchResults = Course.objects.none()

        # query input check
        query = self.request.query_params.get('query', None)
        if (query is None or not query.isalnum()):
            return list(searchResults)

        dateDic = {
            "monday":"MON",
            "tuesday":"TUE",
            "wednesday":"WED",
            "thursday":"THU",
            "friday":"FRI",
            "saturday":"SAT",
            "sunday":"SUN"
        }
        # date check
        if (dateDic.get(query)):
            searchResults = Course.objects.search(dateDic[query])
        else:
            searchResults = Course.objects.search(query)

        # course filter
        courseFilter = self.request.query_params.get('courseTypeFilter', None)
        if (courseFilter is not None):
            if (courseFilter == "tutoring"):
                searchResults.filter(max_capacity == 1)
            if (courseFilter == "group"):
                searchResults.filter(max_capacity <= 5) 
            if (courseFilter == "class"):
                searchResults.filter(max_capacity > 5)

        # availability filter
        availabilityFilter = self.request.query_params.get('availability', None)
        if (availabilityFilter is not None and (availabilityFilter == "open" or availabilityFilter == "filled")):
            # calculate availability
            course_ids = []
            for course in searchResults:
                capacity = len(Enrollment.objects.filter(course = course.id))
                if (availabilityFilter == "open" and capacity < course.max_capacity):
                    course_ids.append(course.id)
                if (availabilityFilter == "filled" and capacity >= course.max_capacity):
                    course_ids.append(course.id)
            searchResults = Course.objects.filter(id__in = course_ids)        
            
        # sort results
        sortFilter = self.request.query_params.get('sort', None)
        if (sortFilter is not None):
            if (sortFilter == "dateAsc"):
                searchResults = searchResults.order_by("start_date")
            if (sortFilter == "dateDesc"):
                searchResults = searchResults.order_by("-start_date")
            if (sortFilter == "timeAsc"):
                searchResults = searchResults.order_by("start_time")
            if (sortFilter == "timeDesc"):
                searchResults = searchResults.order_by("-start_time")
        return list(searchResults)

'''
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
'''
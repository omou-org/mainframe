from itertools import chain
from rest_framework import generics
from rest_framework.response import Response
from operator import attrgetter

from account.models import (
    Student,
    StudentManager,
    Instructor,
    InstructorManager,
    Parent,
    ParentManager,
    Admin,
    AdminManager
)

from course.models import (
    Course,
    Enrollment
)

from search.serializers import SearchViewSerializer

class AccountsSearchView(generics.ListAPIView): 
    serializer_class = SearchViewSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        responseDict = {}
        responseDict["count"] = request.session["count"]
        responseDict["page"] = request.session["page"]
        responseDict["results"] = response.data
        return Response(responseDict)

    def get_queryset(self):
        searchResults = Student.objects.none()

        # query input check
        queries = self.request.query_params.get('query', None)
        if queries is None or False in [query.isalnum() for query in queries.split()]:
            return list(searchResults)

        # query with profile filter
        profileFilter = self.request.query_params.get('profile', None)
        if profileFilter is not None:
            filterToSearch = {
                "student" : getattr(StudentManager, "search"),
                "instructor" : getattr(InstructorManager, "search"),
                "parent" : getattr(ParentManager, "search"),
                "admin" : getattr(AdminManager, "search"),
            }
            filterToModel = {
                "student" : Student.objects,
                "instructor" : Instructor.objects,
                "parent" : Parent.objects,
                "admin" : Admin.objects
            }

            for query in queries.split():
                if filterToSearch.get(profileFilter):
                    searchResults = filterToSearch[profileFilter](filterToModel[profileFilter], query, searchResults)
            
            if profileFilter == "student":
                try:
                    gradeFilter = int(self.request.query_params.get('grade', None))
                    if 1 <= gradeFilter and gradeFilter <= 13:
                        searchResults = Student.objects.filter(grade=gradeFilter)
                except:
                    pass

        # query on all models
        else:
            studentSearchResults = Student.objects.none()
            instructorSearchResults = Instructor.objects.none()
            adminSearchResults = Admin.objects.none()
            for query in queries.split():
                studentSearchResults = Student.objects.search(query, studentSearchResults)
                instructorSearchResults = Instructor.objects.search(query, instructorSearchResults)
                adminSearchResults = Admin.objects.search(query, adminSearchResults)
            searchResults = chain(studentSearchResults, instructorSearchResults, adminSearchResults)

        # sort results
        sortFilter = self.request.query_params.get('sort', None)
        if sortFilter is not None:
            if sortFilter == "alphaAsc":
                searchResults = sorted(searchResults, key=attrgetter('user.first_name','user.last_name'))
            elif sortFilter == "alphaDesc":
                searchResults = sorted(searchResults, key=attrgetter('user.first_name','user.last_name'), reverse=True)
            elif sortFilter == "idAsc":
                searchResults = sorted(searchResults, key=lambda obj:obj.user.id)
            elif sortFilter == "idDesc": 
                searchResults = sorted(searchResults, key=lambda obj:obj.user.id, reverse=True)
            elif sortFilter == "updateAsc":
                searchResults = sorted(searchResults, key=lambda obj:obj.updated_at)
            elif sortFilter == "updateDesc":
                searchResults = sorted(searchResults, key=lambda obj:obj.updated_at, reverse=True)

        searchResults = list(searchResults)
        self.request.session["count"] = len(searchResults)

        # extract searches in page range. Out of bounds page returns nothing
        pageFilter = self.request.query_params.get('page', None)
        self.request.session["page"] = pageFilter
        if pageFilter is not None:
            try:
                pageNumber = int(pageFilter)
                pageSize = 8
                resultLen = len(searchResults)
                rangeEnd = pageSize*pageNumber
                if pageNumber > 0 and rangeEnd-pageSize < resultLen:
                    searchResults = searchResults[rangeEnd-pageSize : resultLen if resultLen <= rangeEnd else rangeEnd]
                else:
                    searchResults = Student.objects.none()
            except ValueError:
                pass

        return searchResults


class CoursesSearchView(generics.ListAPIView):
    serializer_class = SearchViewSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        responseDict = {}
        responseDict["count"] = request.session["count"]
        responseDict["page"] = request.session["page"]
        responseDict["results"] = response.data
        return Response(responseDict)

    def get_queryset(self):
        searchResults = Course.objects.none()

        # query input check
        query = self.request.query_params.get('query', None)
        if query is None or False in [word.isalnum() for word in query.split()]:
            return list(searchResults) 

        for word in query.split():
            dayOfWeekDic = {
                "monday":"MON",
                "tuesday":"TUE",
                "wednesday":"WED",
                "thursday":"THU",
                "friday":"FRI",
                "saturday":"SAT",
                "sunday":"SUN"
            }
            # date check
            if dayOfWeekDic.get(word.lower()):
                word = dayOfWeekDic.get(word.lower())
            searchResults = Course.objects.search(word, searchResults)

        # course filter
        courseFilter = self.request.query_params.get('course', None)
        if courseFilter is not None:
            if courseFilter == "tutoring":
                searchResults = searchResults.filter(max_capacity = 1)
            if courseFilter == "group":
                searchResults = searchResults.filter(max_capacity__lte = 5) 
            if courseFilter == "class":
                searchResults = searchResults.filter(max_capacity__gt = 5)
        
        # size filter
        sizeFilter = self.request.query_params.get('size', None)
        if sizeFilter is not None:
            size = int(sizeFilter)
            course_ids = []
            for course in searchResults:
                curr_size = len(Enrollment.objects.filter(course = course.id))
                if curr_size <= size:
                    course_ids.append(course.id)
            searchResults = Course.objects.filter(id__in = course_ids) 

        # availability filter
        availabilityFilter = self.request.query_params.get('availability', None)
        if availabilityFilter is not None and (availabilityFilter == "open" or availabilityFilter == "filled"):
            # calculate availability
            course_ids = []
            for course in searchResults:
                capacity = len(Enrollment.objects.filter(course = course.id))
                if availabilityFilter == "open" and capacity < course.max_capacity:
                    course_ids.append(course.id)
                if availabilityFilter == "filled" and capacity >= course.max_capacity:
                    course_ids.append(course.id)
            searchResults = Course.objects.filter(id__in = course_ids)        
            
        # sort results
        sortFilter = self.request.query_params.get('sort', None)
        if sortFilter is not None:
            sortToParameter = {
                "dateAsc":"start_date",
                "dateDesc":"-start_date",
                "timeAsc":"start_time",
                "timeDesc":"-start_time"
            }
            if sortToParameter.get(sortFilter):
                searchResults = searchResults.order_by(sortToParameter[sortFilter])

        searchResults = list(searchResults)
        self.request.session["count"] = len(searchResults)

        # extract searches in page range
        pageFilter = self.request.query_params.get('page', None)
        self.request.session["page"] = pageFilter
        if pageFilter is not None:
            try:
                pageNumber = int(pageFilter)
                pageSize = 8
                resultLen = len(searchResults)
                rangeEnd = pageSize*pageNumber
                if pageNumber > 0 and rangeEnd-pageSize < resultLen:
                    searchResults = searchResults[rangeEnd-pageSize : resultLen if resultLen <= rangeEnd else rangeEnd]
                else:
                    searchResults = Course.objects.none()
            except ValueError:
                pass

        return searchResults

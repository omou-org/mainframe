import graphene
from graphene import Field, Int, List, String
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model

from itertools import chain
from operator import attrgetter
from datetime import datetime
import pytz

from account.schema import (
    UserInfoType
)
from account.models import (
    Student,
    Instructor,
    Parent,
    Admin,
)
from account.managers import (
    StudentManager,
    InstructorManager,
    ParentManager,
    AdminManager
)

from course.models import (
    Course,
    Enrollment
)
from course.schema import (
    CourseType
)

from scheduler.models import (
    Session
)
from scheduler.schema import (
    SessionType
)


def paginate(results, page, size):
    if page is not None and size is not None:
        try:
            size = int(size)
            page = int(page)
            total_len = len(results)
            range_end = size*page # max number of results that fit entirely within page size
            if page > 0 and range_end-size < total_len:
                results = results[range_end-size : total_len if total_len <= range_end else range_end]
            else:
                return []
        except ValueError:
            pass
    return results


class AccountSearchResults(graphene.ObjectType):
    results = List(UserInfoType, required=True)
    total = Int()
 

class CourseSearchResults(graphene.ObjectType):
    results = List(CourseType, required=True)
    total = Int()   


class SessionSearchResults(graphene.ObjectType):
    results = List(SessionType, required=True)
    total = Int()


class Query(object):
    accountSearch = Field(AccountSearchResults,
                        query=String(required=True),
                        profile=String(),
                        grade=Int(),
                        sort=String(),
                        page=Int(),
                        page_size=Int()
                        )

    courseSearch = Field(CourseSearchResults,
                        query=String(required=True),
                        course_type=String(),
                        course_size=Int(),
                        availability=String(),
                        sort=String(),
                        page=Int(),
                        page_size=Int()
                        )
    
    sessionSearch = Field(SessionSearchResults,
                        query=String(required=True),
                        time=String(),
                        sort=String(),
                        page=Int(),
                        page_size=Int()
                        )
    
    def resolve_accountSearch(self, info, **kwargs):        
        results = Student.objects.none()
        query = kwargs.get('query')

        # query with profile filter
        profile = kwargs.get('profile', None)
        if profile is not None:
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

            for token in query.split():
                if filterToSearch.get(profile):
                    results = filterToSearch[profile](filterToModel[profile], token, results)
            
            if profile == "student":
                try:
                    grade = int(kwargs.get('grade', None))
                    if 1 <= grade and grade <= 13:
                        results = Student.objects.filter(grade=grade)
                except:
                    pass
        
        # query on all models
        else:
            student_results = Student.objects.none()
            parent_results = Parent.objects.none()
            instructor_results = Instructor.objects.none()
            admin_results = Admin.objects.none()
            for token in query.split():
                student_results = Student.objects.search(token, student_results)
                parent_results = Parent.objects.search(token, parent_results)
                instructor_results = Instructor.objects.search(token, instructor_results)
                admin_results = Admin.objects.search(token, admin_results)
            results = chain(student_results, parent_results, instructor_results, admin_results)

        # sort results
        sort = kwargs.get('sort', None)
        if sort is not None:
            if sort == "alphaAsc":
                results = sorted(results, key=attrgetter('user.first_name','user.last_name'))
            elif sort == "alphaDesc":
                results = sorted(results, key=attrgetter('user.first_name','user.last_name'), reverse=True)
            elif sort == "idAsc":
                results = sorted(results, key=lambda obj:obj.user.id)
            elif sort == "idDesc": 
                results = sorted(results, key=lambda obj:obj.user.id, reverse=True)
            elif sort == "updateAsc":
                results = sorted(results, key=lambda obj:obj.updated_at)
            elif sort == "updateDesc":
                results = sorted(results, key=lambda obj:obj.updated_at, reverse=True)

        total = len(results)
        results = list(results)
        results = paginate(results, kwargs.get('page', None), kwargs.get('page_size', None))

        return AccountSearchResults(
            results = results,
            total = total
        )
    

    def resolve_courseSearch(self, info, **kwargs):
        results = Course.objects.none()
        query = kwargs.get('query') 

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
            results = Course.objects.search(word, results)

        # course filter
        course_type = kwargs.get('course_type', None)
        if course_type is not None:
            if course_type == "tutoring":
                results = results.filter(max_capacity = 1)
            if course_type == "group":
                results = results.filter(max_capacity__lte = 5, max_capacity__gt = 1) 
            if course_type == "class":
                results = results.filter(max_capacity__gt = 5)
        
        # size filter
        course_size = kwargs.get('course_size', None)
        if course_size is not None:
            course_size = int(course_size)
            course_ids = []
            for course in results:
                curr_size = len(Enrollment.objects.filter(course = course.id))
                if curr_size <= course_size:
                    course_ids.append(course.id)
            results = Course.objects.filter(id__in = course_ids) 

        # availability filter
        availability = kwargs.get('availability', None)
        if availability is not None and (availability == "open" or availability == "filled"):
            # calculate availability
            course_ids = []
            for course in results:
                capacity = len(Enrollment.objects.filter(course = course.id))
                if availability == "open" and capacity < course.max_capacity:
                    course_ids.append(course.id)
                if availability == "filled" and capacity >= course.max_capacity:
                    course_ids.append(course.id)
            results = Course.objects.filter(id__in = course_ids)        
            
        # sort results
        sort = kwargs.get('sort', None)
        if sort is not None:
            sortToParameter = {
                "dateAsc":"start_date",
                "dateDesc":"-start_date",
                "timeAsc":"start_time",
                "timeDesc":"-start_time"
            }
            if sortToParameter.get(sort):
                results = results.order_by(sortToParameter[sort])

        total = len(results)
        results = list(results)
        results = paginate(results, kwargs.get('page', None), kwargs.get('page_size', None))

        return CourseSearchResults(
            results = results,
            total = total
        )


    def resolve_sessionSearch(self, info, **kwargs):
        results = Session.objects.all()

        query = kwargs.get('query', None)
        if query is not None:
            for word in query.split():
                results = Session.objects.search(word, results)
        
        # time filter
        time = kwargs.get('time', None)
        if time is not None: # all is default
            if time == "future":
                results = results.filter(start_datetime__gte = datetime.utcnow())
            elif time == "past":
                results = results.filter(start_datetime__lte = datetime.utcnow())
            elif time == "today":
                results = results.filter(start_datetime__date = datetime.utcnow())

        # sort results
        sort = kwargs.get('sort', None)
        if sort is not None:
            sortToParameter = {
                "timeAsc":"start_datetime",
                "timeDesc":"-start_datetime"
            }
            if sortToParameter.get(sort):
                results = results.order_by(sortToParameter[sort])
        
        total = len(results)
        results = list(results)
        results = paginate(results, kwargs.get('page', None), kwargs.get('page_size', None))

        return SessionSearchResults(
            results = results,
            total = total
        )
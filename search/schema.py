import graphene
from graphene import Field, Int, List, String
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required

from itertools import chain
from operator import attrgetter
from datetime import datetime
import pytz

from account.schema import UserInfoType
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
    AdminManager,
)

from course.models import Course, Enrollment
from course.schema import CourseType

from scheduler.models import Session
from scheduler.schema import SessionType


def paginate(results, page, size):
    if page and size:
        try:
            size = int(size)
            page = int(page)
            total_len = len(results)
            range_end = (
                size * page
            )  # max number of results that fit entirely within page size
            if page > 0 and range_end - size < total_len:
                results = results[
                    range_end - size : total_len
                    if total_len <= range_end
                    else range_end
                ]
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
    accountSearch = Field(
        AccountSearchResults,
        query=String(required=True),
        profile=String(),
        grade=Int(),
        sort=String(),
        page=Int(),
        page_size=Int(),
    )

    courseSearch = Field(
        CourseSearchResults,
        query=String(required=True),
        course_type=String(),
        course_size=Int(),
        availability=String(),
        sort=String(),
        page=Int(),
        page_size=Int(),
    )

    sessionSearch = Field(
        SessionSearchResults,
        query=String(required=True),
        time=String(),
        sort=String(),
        page=Int(),
        page_size=Int(),
    )

    @login_required
    def resolve_accountSearch(self, info, **kwargs):
        # access control results based on user type
        user_id = info.context.user.id

        is_student = Student.objects.filter(user=user_id).exists()
        is_instructor = Instructor.objects.filter(user=user_id).exists()
        is_parent = Parent.objects.filter(user=user_id).exists()
        if is_student:
            profiles = ["ADMIN", "INSTRUCTOR", "PARENT"]
        elif is_instructor:
            profiles = ["ADMIN", "INSTRUCTOR", "PARENT", "STUDENT"]
        elif is_parent:
            profiles = ["ADMIN", "INSTRUCTOR", "STUDENT"]
        else:  # admin
            profiles = ["ADMIN", "PARENT", "INSTRUCTOR", "STUDENT"]

        # query on profile filter if set else all account types
        profile = kwargs.get("profile", None)
        if profile in profiles:  # only use profile if accessible
            profiles = [profile]

        # define filter param to django manager/object mappings
        filterToSearch = {
            "STUDENT": getattr(StudentManager, "search"),
            "INSTRUCTOR": getattr(InstructorManager, "search"),
            "PARENT": getattr(ParentManager, "search"),
            "ADMIN": getattr(AdminManager, "search"),
        }
        filterToModel = {
            "STUDENT": Student.objects,
            "INSTRUCTOR": Instructor.objects,
            "PARENT": Parent.objects,
            "ADMIN": Admin.objects,
        }
        # set results and query
        results = Student.objects.none()
        query = kwargs.get("query")

        # iterate over account types to search
        for profile in profiles:
            profile_results = filterToModel[profile].none()

            # filter for ADMIN if profile is admin type
            admin_profile = None
            if profile.lower() in [t[0] for t in Admin.TYPE_CHOICES]:
                admin_profile = profile.lower()
                profile = "ADMIN"

            for token in query.split():
                if filterToSearch.get(profile):
                    profile_results = filterToSearch[profile](
                        filterToModel[profile], token, profile_results
                    )

            # filter for admin types
            if admin_profile is not None:
                profile_results = profile_results.filter(admin_type=admin_profile)

            if profile == "STUDENT":
                # filter for grade if STUDENT
                try:
                    grade = int(kwargs.get("grade", None))
                    if 1 <= grade and grade <= 13:
                        profile_results = profile_results.filter(grade=grade)
                except:
                    pass

                # students in instructor's courses
                if is_instructor:
                    courses = Course.objects.filter(instructor=user_id)
                    student_ids = set()
                    for course in courses:
                        student_ids.update(course.enrollment_list)
                    profile_results = profile_results.filter(user_id__in=student_ids)

                # parent's students
                if is_parent:
                    parent = Parent.objects.get(user=user_id)
                    profile_results = profile_results.filter(
                        user_id__in=parent.student_list
                    )

            # parent
            if profile == "PARENT":
                # parents of students in instructor's courses
                if is_instructor:
                    # find students
                    courses = Course.objects.filter(instructor=user_id)
                    student_ids = set()
                    for course in courses:
                        student_ids.update(course.enrollment_list)

                    # students' parents
                    parent_ids = set()
                    for student_id in student_ids:
                        student = Student.objects.get(user_id=student_id)
                        if student.primary_parent:
                            parent_ids.add(student.primary_parent.user.id)
                        if student.secondary_parent:
                            parent_ids.add(student.secondary_parent.user.id)
                    profile_results = profile_results.filter(user_id__in=parent_ids)

                # student's parents
                if is_student:
                    student = Student.objects.get(user=user_id)
                    primary_parent_id = (
                        None
                        if not student.primary_parent
                        else student.primary_parent.user.id
                    )
                    secondary_parent_id = (
                        None
                        if not student.secondary_parent
                        else student.primary_parent.user.id
                    )
                    profile_results = profile_results.filter(
                        user_id__in=[primary_parent_id, secondary_parent_id]
                    )

            results = chain(results, profile_results)

        # sort results
        sort = kwargs.get("sort", None)
        if sort is not None:
            if sort == "alphaAsc":
                results = sorted(
                    results, key=attrgetter("user.first_name", "user.last_name")
                )
            elif sort == "alphaDesc":
                results = sorted(
                    results,
                    key=attrgetter("user.first_name", "user.last_name"),
                    reverse=True,
                )
            elif sort == "idAsc":
                results = sorted(results, key=lambda obj: obj.user.id)
            elif sort == "idDesc":
                results = sorted(results, key=lambda obj: obj.user.id, reverse=True)
            elif sort == "updateAsc":
                results = sorted(results, key=lambda obj: obj.updated_at)
            elif sort == "updateDesc":
                results = sorted(results, key=lambda obj: obj.updated_at, reverse=True)

        results = list(results)
        total = len(results)
        results = paginate(
            results, kwargs.get("page", None), kwargs.get("page_size", None)
        )

        return AccountSearchResults(results=results, total=total)

    @login_required
    def resolve_courseSearch(self, info, **kwargs):
        results = Course.objects.none()
        query = kwargs.get("query")

        for word in query.split():
            dayOfWeekDic = {
                "monday": "MON",
                "tuesday": "TUE",
                "wednesday": "WED",
                "thursday": "THU",
                "friday": "FRI",
                "saturday": "SAT",
                "sunday": "SUN",
            }
            # date check
            if dayOfWeekDic.get(word.lower()):
                word = dayOfWeekDic.get(word.lower())
            results = Course.objects.search(word, results)

        # course filter
        course_type = kwargs.get("course_type", None)
        if course_type is not None:
            if course_type == "tutoring":
                results = results.filter(max_capacity=1)
            if course_type == "group":
                results = results.filter(max_capacity__lte=5, max_capacity__gt=1)
            if course_type == "class":
                results = results.filter(max_capacity__gt=5)

        # size filter
        course_size = kwargs.get("course_size", None)
        if course_size is not None:
            course_size = int(course_size)
            course_ids = []
            for course in results:
                curr_size = len(Enrollment.objects.filter(course=course.id))
                if curr_size <= course_size:
                    course_ids.append(course.id)
            results = Course.objects.filter(id__in=course_ids)

        # availability filter
        availability = kwargs.get("availability", None)
        if availability is not None and (
            availability == "open" or availability == "filled"
        ):
            # calculate availability
            course_ids = []
            for course in results:
                capacity = len(Enrollment.objects.filter(course=course.id))
                if availability == "open" and capacity < course.max_capacity:
                    course_ids.append(course.id)
                if availability == "filled" and capacity >= course.max_capacity:
                    course_ids.append(course.id)
            results = Course.objects.filter(id__in=course_ids)

        # sort results
        sort = kwargs.get("sort", None)
        if sort is not None:
            sortToParameter = {
                "dateAsc": "start_date",
                "dateDesc": "-start_date",
                "timeAsc": "start_time",
                "timeDesc": "-start_time",
            }
            if sortToParameter.get(sort):
                results = results.order_by(sortToParameter[sort])

        results = list(results)
        total = len(results)
        results = paginate(
            results, kwargs.get("page", None), kwargs.get("page_size", None)
        )

        return CourseSearchResults(results=results, total=total)

    @login_required
    def resolve_sessionSearch(self, info, **kwargs):
        results = Session.objects.all()

        query = kwargs.get("query", None)
        if query is not None:
            for word in query.split():
                results = Session.objects.search(word, results)

        # time filter
        time = kwargs.get("time", None)
        if time is not None:  # all is default
            if time == "future":
                results = results.filter(start_datetime__gte=datetime.utcnow())
            elif time == "past":
                results = results.filter(start_datetime__lte=datetime.utcnow())
            elif time == "today":
                results = results.filter(start_datetime__date=datetime.utcnow())

        # sort results
        sort = kwargs.get("sort", None)
        if sort is not None:
            sortToParameter = {
                "timeAsc": "start_datetime",
                "timeDesc": "-start_datetime",
            }
            if sortToParameter.get(sort):
                results = results.order_by(sortToParameter[sort])

        results = list(results)
        total = len(results)
        results = paginate(
            results, kwargs.get("page", None), kwargs.get("page_size", None)
        )

        return SessionSearchResults(results=results, total=total)

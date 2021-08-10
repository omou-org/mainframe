from datetime import datetime, timedelta, timezone
import arrow
import calendar
import pytz

from django.db.models import Q
from graphene import Boolean, Field, ID, Int, List, String, DateTime, Time, Float
from graphene_django.types import DjangoObjectType, ObjectType
from graphql_jwt.decorators import login_required

from account.schema import InstructorType

from account.models import (
    Admin,
    Instructor,
    Parent,
    Student,
    InstructorAvailability,
    InstructorOutOfOffice,
    UserInfo,
)

from course.models import Course, Enrollment
from scheduler.models import Session, SessionNote, Attendance
from scheduler.utilities import get_instructor_tutoring_availablity


class SessionType(DjangoObjectType):
    class Meta:
        model = Session


class SessionNoteType(DjangoObjectType):
    class Meta:
        model = SessionNote


class TutoringAvailabilitiesType(ObjectType):
    monday = List(Time)
    tuesday = List(Time)
    wednesday = List(Time)
    thursday = List(Time)
    friday = List(Time)
    saturday = List(Time)
    sunday = List(Time)


class InstructorTutoringAvailabilitiesType(ObjectType):
    instructor = Field(InstructorType)
    tutoring_availability = Field(TutoringAvailabilitiesType)


class ValidateScheduleType(ObjectType):
    status = Boolean()
    reason = String()


class AttendanceType(DjangoObjectType):
    class Meta:
        model = Attendance


class Query(object):
    session = Field(SessionType, session_id=ID(required=True))
    sessions = List(
        SessionType,
        time_frame=String(),
        view_option=String(),
        course_id=ID(),
        time_shift=Int(default_value=0),
        user_id=ID(),
        start_date=String(),
        end_date=String(),
    )
    session_note = Field(SessionNoteType, note_id=ID())
    session_notes = List(SessionNoteType, session_id=ID(required=True))
    attendance = Field(AttendanceType, attendance_id=ID(required=True))
    attendances = List(AttendanceType, course_id=ID())

    # Schedule validators
    validate_session_schedule = Field(
        ValidateScheduleType,
        instructor_id=ID(required=True),
        start_time=String(required=True),
        end_time=String(required=True),
        date=String(required=True),
    )
    validate_course_schedule = Field(
        ValidateScheduleType,
        instructor_id=ID(required=True),
        start_time=String(required=True),
        end_time=String(required=True),
        start_date=String(required=True),
        end_date=String(required=True),
    )

    # Tutoring Availability query
    instructor_tutoring_availablity = List(
        InstructorTutoringAvailabilitiesType,
        start_date=String(required=True),
        end_date=String(required=True),
        duration=Float(required=True),
        topic=ID(required=True),
    )

    @login_required
    def resolve_session(self, info, session_id):
        return Session.objects.get(id=session_id)

    @login_required
    def resolve_sessions(
        self,
        info,
        time_frame=None,
        view_option=None,
        course_id=None,
        time_shift=0,
        user_id=None,
        start_date=None,
        end_date=None,
    ):
        queryset = Session.objects.all()

        if course_id is not None:
            queryset = queryset.filter(course=course_id)

        # instructor
        if Instructor.objects.filter(user__id=user_id).exists():
            queryset = queryset.filter(instructor=user_id)

        # student
        if Student.objects.filter(user__id=user_id).exists():
            # get all courses student is enrolled in
            courses = [
                enrollment.course
                for enrollment in Enrollment.objects.filter(student=user_id)
            ]
            # filter sessions to only those of courses student is enrolled in
            queryset = queryset.filter(course__in=courses)

        # parent
        if Parent.objects.filter(user__id=user_id).exists():
            parent = Parent.objects.get(user_id=user_id)
            # get all courses children are enrolled in
            courses = set()
            for student_id in parent.student_list:
                for enrollment in Enrollment.objects.filter(student=student_id):
                    courses.add(enrollment.course)
            # filter sessions to only those of courses children are enrolled in
            queryset = queryset.filter(course__in=courses)

        if view_option == "class":
            queryset = queryset.filter(course__course_type=Course.CLASS)
        elif view_option == "tutoring":
            queryset = queryset.filter(
                Q(course__course_type=Course.TUTORING)
                | Q(course__course_type=Course.SMALL_GROUP)
            )

        now = datetime.now(tz=pytz.timezone("America/Los_Angeles"))
        base = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if time_frame == "day":
            start_of_day = base + timedelta(days=time_shift)
            end_of_day = start_of_day + timedelta(days=1)
            queryset = queryset.filter(
                start_datetime__gte=start_of_day, end_datetime__lt=end_of_day
            )
        elif time_frame == "week":
            start_of_week = base - timedelta(days=(base.weekday() + 1) % 7)
            start_of_week += timedelta(days=7 * time_shift)
            end_of_week = start_of_week + timedelta(days=7)
            queryset = queryset.filter(
                start_datetime__gte=start_of_week, end_datetime__lt=end_of_week
            )
        elif time_frame == "month":
            start_of_month = base.replace(day=1)
            start_of_month = arrow.get(start_of_month).shift(months=time_shift).datetime
            if start_of_month.month == 12:
                end_of_month = start_of_month.replace(
                    year=start_of_month.year + 1, month=1
                )
            else:
                end_of_month = start_of_month.replace(month=start_of_month.month + 1)
            queryset = queryset.filter(
                start_datetime__gte=start_of_month, end_datetime__lt=end_of_month
            )

        if start_date is not None and end_date is not None:
            queryset = queryset.filter(
                start_datetime__gte=arrow.get(start_date).datetime,
                end_datetime__lt=arrow.get(end_date).datetime,
            )

        queryset = queryset.order_by("start_datetime")
        return queryset

    @login_required
    def resolve_session_note(self, info, **kwargs):
        note_id = kwargs.get("note_id")

        if note_id:
            return SessionNote.objects.get(id=note_id)

        return None

    @login_required
    def resolve_session_notes(self, info, **kwargs):
        session_id = kwargs.get("session_id")

        return SessionNote.objects.filter(session_id=session_id)

    @login_required
    def resolve_validate_session_schedule(
        self, info, instructor_id, start_time, end_time, date
    ):
        datetime_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = calendar.day_name[datetime_obj.weekday()].lower()
        start_datetime = datetime.combine(
            datetime_obj.date(), datetime.strptime(start_time, "%H:%M").time()
        )
        end_datetime = datetime.combine(
            datetime_obj.date(), datetime.strptime(end_time, "%H:%M").time()
        )
        start_datetime = (
            pytz.timezone("America/Los_Angeles")
            .localize(start_datetime)
            .astimezone(pytz.utc)
        )
        end_datetime = (
            pytz.timezone("America/Los_Angeles")
            .localize(end_datetime)
            .astimezone(pytz.utc)
        )

        # Check availabilities
        instructor_availabilities = InstructorAvailability.objects.filter(
            instructor=instructor_id,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time,
        )

        if not instructor_availabilities:
            return {
                "status": False,
                "reason": "The instructor is not marked for being "
                "available at this day of week and time.",
            }

        # Check conflicting sessions
        sessions = Session.objects.filter(
            Q(course__instructor=instructor_id),
            (Q(start_datetime__gte=start_datetime) & Q(start_datetime__lt=end_datetime))
            | (
                Q(start_datetime__lte=start_datetime)
                & Q(end_datetime__gt=start_datetime)
            ),
        )

        if sessions:
            return {
                "status": False,
                "reason": f"The instructor is teaching a session for the "
                f"following course at the selected time: "
                f'"{sessions[0].course.subject}"',
            }

        # Check out of office
        out_of_office = InstructorOutOfOffice.objects.filter(
            Q(instructor=instructor_id),
            (Q(start_datetime__gte=start_datetime) & Q(start_datetime__lt=end_datetime))
            | (
                Q(start_datetime__lte=start_datetime)
                & Q(end_datetime__gt=start_datetime)
            ),
        )

        if out_of_office:
            return {
                "status": False,
                "reason": f"The instructor is marked out of office at that time.",
            }

        return {"status": True}

    @login_required
    def resolve_validate_course_schedule(
        self, info, instructor_id, start_time, end_time, start_date, end_date
    ):
        start_datetime_obj = datetime.strptime(start_date, "%Y-%m-%d")
        day_of_week = calendar.day_name[start_datetime_obj.weekday()].lower()

        # Check availabilities
        instructor_availabilities = InstructorAvailability.objects.filter(
            instructor=instructor_id,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time,
        )

        if not instructor_availabilities:
            return {
                "status": False,
                "reason": "The instructor is not marked for being "
                "available at this day of week and time.",
            }

        # Check conflicting courses
        courses = Course.objects.filter(
            Q(instructor=instructor_id),
            Q(day_of_week=day_of_week),
            (
                Q(start_date__gte=start_date) & Q(start_date__lt=end_date)
                | Q(start_date__lte=start_date) & Q(end_date__gt=start_date)
            ),
            (
                Q(start_time__gte=start_time) & Q(start_time__lt=end_time)
                | Q(start_time__lte=start_time) & Q(end_time__gt=start_time)
            ),
        )

        if courses:
            return {
                "status": False,
                "reason": f"The instructor already is teaching the following "
                f"course during those days and times: "
                f'"{courses[0].subject}"',
            }

        return {"status": True}

    @login_required
    def resolve_attendance(self, info, attendance_id):
        return Attendance.objects.get(id=attendance_id)

    @login_required
    def resolve_attendances(self, info, course_id=None):
        queryset = Attendance.objects.all()
        if course_id is not None:
            queryset = queryset.filter(session__course=course_id)

        return queryset

    @login_required
    def resolve_instructor_tutoring_availablity(
        self,
        info,
        start_date,
        end_date,
        duration,
        topic,
    ):

        user = Parent.objects.get(user=info.context.user)
        business_id = user.business.id
        queryset = Instructor.objects.all()

        if topic is not None:
            queryset = queryset.filter(subjects=topic)

        sd = datetime.strptime(start_date, "%Y-%d-%m")
        ed = datetime.strptime(end_date, "%Y-%d-%m")
        new_start_date = datetime(sd.year, sd.month, sd.day, tzinfo=timezone.utc)
        new_end_date = datetime(ed.year, ed.month, ed.day, tzinfo=timezone.utc)

        tutoring_availabilities = []
        for instructor in queryset:
            instructor_id = instructor.user.id
            tutoring_availabilities.append(
                {
                    "instructor": queryset.get(user=instructor_id),
                    "tutoring_availability": get_instructor_tutoring_availablity(
                        instructor_id,
                        business_id,
                        new_start_date,
                        new_end_date,
                        duration,
                    ),
                }
            )

        return tutoring_availabilities

from datetime import datetime, time, timedelta, date
from typing import final
from account.models import (
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from onboarding.models import Business
from scheduler.models import Session
from django.utils.timezone import make_aware
from django.utils import timezone
from course.models import Course


def time_to_index(time: datetime, day_of_week: str, business_id: int) -> int:
    # index = time - start_time/ 30 min
    business = Business.objects.get(id=business_id)
    start_time = business.availability_list.get(day_of_week=day_of_week).start_time
    today = datetime.today()
    selected_time = datetime.combine(today, time)
    business_start_time = datetime.combine(today, start_time)
    difference = selected_time - business_start_time
    minutes = difference.total_seconds() / 60
    index = minutes / 30
    return int(index)


def index_to_time(index: int, day_of_week: str, business_id: int) -> datetime:
    business = Business.objects.get(id=business_id)
    start_time = business.availability_list.get(day_of_week=day_of_week).start_time
    today = datetime.today()
    business_start_time = (datetime.combine(today, start_time)).time()
    minutes = business_start_time.hour * 60 + business_start_time.minute
    total_minutes = minutes + (30 * index)
    final_time = timedelta(minutes=total_minutes)
    return final_time


def duration_to_boolean_list(start_time, end_time):
    today = datetime.today()
    start_time = datetime.combine(today, start_time)
    end_time = datetime.combine(today, end_time)
    difference = end_time - start_time
    total_minutes = difference.total_seconds() / 60
    index = total_minutes / 30
    return [True] * int(index)


def get_buessiness_hours_map(buesiness_id: int) -> dict:
    availability_dict = {}
    business = Business.objects.get(id=buesiness_id)
    avail = business.availability_list.all()

    for e in avail:
        if e.day_of_week not in availability_dict:
            availability_dict[e.day_of_week] = duration_to_boolean_list(
                e.start_time, e.end_time
            )

    return availability_dict


def get_instructor_sessions(instructor_id: int, start_date, end_date) -> list:
    weekdays = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    instructor_availabilities_dict = {}
    instructor_sessions = Session.objects.filter(
        start_datetime__range=(start_date, end_date),
        end_datetime__range=(start_date, end_date),
        instructor_id=instructor_id,
    )

    # Need to get start & end time of course
    instructor_availability = InstructorAvailability.instructor
    print(instructor_availability.instructor)

    for e in instructor_sessions:
        if weekdays[e.start_datetime.weekday()] not in instructor_availabilities_dict:
            instructor_availabilities_dict[weekdays[e.start_datetime.weekday()]] = 1

    print(instructor_availabilities_dict)


def set_instructor_business_availabilities(instructor_id: int) -> dict:
    pass


def get_instructor_availabilities(instructor_id: int, start_date, end_date) -> dict:
    # given an instructor ID and a start & end time
    # return an object with possible availabilities
    # get business hours map
    #
    pass


st = time(10, 0)
et = time(11, 00)
sd = datetime(2020, 1, 26, 10, 0, tzinfo=timezone.utc)
ed = datetime(2021, 10, 15, 11, 0, tzinfo=timezone.utc)
# print(get_instructor_availabilities(2, sd, ed))
print(get_instructor_sessions(5, sd, ed))
# print(get_buessiness_hours_map(buesiness_id=1))
# print(index_to_time(1, "monday", 1))
# print(time_to_index(selected_time, "monday", 1))

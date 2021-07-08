from datetime import datetime, time, timedelta, date
from typing import final
from account.models import (
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from onboarding.models import Business


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


def get_buessiness_hours_map(buesiness_id: int) -> dict:
    # create a function that returns a dict of days as keys and array of bools for the amount of hours in a day
    business = Business.objects.get(id=buesiness_id)
    avail = business.availability_list
    r = avail
    print(r)


def set_instructor_availabilities(
    instructor_id: int, instructor_availiablities_map: dict
) -> dict:
    pass


print(get_buessiness_hours_map(buesiness_id=1))
# day = time(10, 30)
# print(index_to_time(9, "monday", 1))
# print(time_to_index(day, "monday", 1))

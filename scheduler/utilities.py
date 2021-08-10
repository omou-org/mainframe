from datetime import datetime, time, timedelta, 
from account.models import (
    Instructor,
    InstructorAvailability,
    InstructorOutOfOffice,
)
from onboarding.models import Business
from scheduler.models import Session



# Converts a python datetime.time() object to an index depending on the business
# hours start time
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


# Converts an index to python timedelta given day of week and business id
def index_to_time(index: int, day_of_week: str, business_id: int) -> datetime:
    business = Business.objects.get(id=business_id)
    start_time = business.availability_list.get(day_of_week=day_of_week).start_time
    today = datetime.today()
    business_start_time = (datetime.combine(today, start_time)).time()
    minutes = business_start_time.hour * 60 + business_start_time.minute
    total_minutes = minutes + (30 * index)
    time_delta = timedelta(minutes=total_minutes)
    final_time = (datetime.min + time_delta).time()
    return final_time


# Returns a list of False given a start and end time
def duration_to_boolean_list(start_time, end_time):
    today = datetime.today()
    start_time = datetime.combine(today, start_time)
    end_time = datetime.combine(today, end_time)
    difference = end_time - start_time
    total_minutes = difference.total_seconds() / 60
    index = total_minutes / 30
    return [False] * int(index)


# Given business id, return a dict of day of week as keys and response of
# duration bool list as the value
def get_business_hours_map(buesiness_id: int) -> dict:
    availability_dict = {}
    business = Business.objects.get(id=buesiness_id)
    avail = business.availability_list.all()

    for e in avail:
        if e.day_of_week not in availability_dict:
            availability_dict[e.day_of_week] = duration_to_boolean_list(
                e.start_time, e.end_time
            )

    return availability_dict


# Gets start and end time of instructors availabilities and sets the values to
# true comparing the business hours
def get_instructor_availabilities(instructor_id: int, business_id: int) -> dict:
    # compares business hours and sets the instructors availability
    instructor_availablilities_map = get_business_hours_map(buesiness_id=business_id)
    # gets instructors availablities
    instructor_availability_dict = InstructorAvailability.objects.filter(
        instructor=instructor_id
    )

    for instructors_availability in instructor_availability_dict:
        day_of_week = instructors_availability.day_of_week
        start_index = time_to_index(
            instructors_availability.start_time,
            instructors_availability.day_of_week,
            business_id,
        )
        end_index = time_to_index(
            instructors_availability.end_time,
            instructors_availability.day_of_week,
            business_id,
        )
        for index in range(start_index, end_index):
            instructor_availablilities_map[day_of_week][index] = True

    return instructor_availablilities_map


# create an object of keys as the day of week and array of unique start times
def find_instructor_teaching_schedule(
    day_of_week, instructor_sessions, business_id, weekdays
):

    # filter all sessions by day of week
    sessions_for_day_of_week = [
        session
        for session in instructor_sessions
        if session.start_datetime.weekday() == day_of_week
    ]

    # return an array of start times
    unique_unavailable_start_times_for_day_of_week = []
    seen = []
    for session in sessions_for_day_of_week:
        if session.availability.start_time not in seen:
            unique_unavailable_start_times_for_day_of_week.append(
                (
                    time_to_index(
                        session.availability.start_time,
                        weekdays[day_of_week],
                        business_id,
                    ),
                    time_to_index(
                        session.availability.end_time,
                        weekdays[day_of_week],
                        business_id,
                    ),
                )
            )
            seen.append(session.availability.start_time)

    # sorts list of tuples
    if len(unique_unavailable_start_times_for_day_of_week) > 0:
        unique_unavailable_start_times_for_day_of_week.sort(key=lambda tup: tup[0])
        return unique_unavailable_start_times_for_day_of_week
    else:
        return []


# Returns a dict of days of week as keys and instructors availability
def get_instructor_tutoring_availablity(
    instructor_id: int,
    business_id: int,
    start_date: datetime,
    end_date: datetime,
    duration: float,
) -> list:
    weekdays = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    # gets instructors availabilities compared to the business hours
    instructor_availabilities_dict = get_instructor_availabilities(
        instructor_id, business_id
    )

    # gets all single instructors sessions between start_date and end_date.
    instructor_sessions = Session.objects.filter(
        start_datetime__range=(start_date, end_date),
        end_datetime__range=(start_date, end_date),
        instructor_id=instructor_id,
    )

    # gets unique start times for each session and stores it in obj
    instructor_teaching_schedule_dict = {}
    for day in range(7):
        if weekdays[day] not in instructor_teaching_schedule_dict:
            instructor_teaching_schedule_dict[
                weekdays[day]
            ] = find_instructor_teaching_schedule(
                day, instructor_sessions, business_id, weekdays
            )


    def find_all_start_time_indices(
            inst_avail_list,
        ):
            counter = 0
            consecutive_index = []
            pos = -1
            for idx, val in enumerate(inst_avail_list):
                if val == True and pos == -1:
                    counter += 1
                    pos = idx
                elif val == True:
                    counter += 1
                elif pos != -1:
                    consecutive_index.append(pos)
                    pos = -1
                    counter = 0
            if counter > 0:
                consecutive_index.append(pos)

            return consecutive_index
    # helper function to set instructor hours
    def set_instructor_availability_map(
        instructor_teaching_schedule, inst_avail_dict, duration
    ):
        duration_map = {
            0.5: 1,
            1.0: 2,
            1.5: 3,
            2.0: 4,
        }

        # loop through business_hours array
        for day in instructor_teaching_schedule:
            for teaching_range in sorted(
                instructor_teaching_schedule[day], key=lambda tup: tup[0]
            ):
                teaching_range_start_index = teaching_range[0]
                teaching_range_end_index = teaching_range[1]
                for time_index in range(
                    teaching_range_start_index, teaching_range_end_index
                ):
                    inst_avail_dict[day][time_index] = False

        
        for day in inst_avail_dict:
            
            # Find all available start time indices
            requested_start_index_list = find_all_start_time_indices(inst_avail_dict[day])
            # For each start time indices
            
            for requested_start_time_index in requested_start_index_list:
                 
                shortest_index_distance = None
                closest_teaching_range = None    
                # Find requested end time index
                requested_end_time_index = requested_start_time_index + duration_map[duration]
                # loops through tuple of instructor session start time & end time indices 
                for instructor_teaching_hours_range in instructor_teaching_schedule_dict[day]:
                    # finds the shortest distances by subtracting the requested end time index with the start time of session

                    current_index_distance = abs(requested_end_time_index - instructor_teaching_hours_range[0])

                    if shortest_index_distance is None or closest_teaching_range is None:
                        closest_teaching_range = instructor_teaching_hours_range
                        shortest_index_distance = current_index_distance

                    if current_index_distance < shortest_index_distance and shortest_index_distance is not None and closest_teaching_range is not None:
                        closest_teaching_range = instructor_teaching_hours_range
                        shortest_index_distance = current_index_distance
                        
                      
                # helper function to set the instructors availability dict output     
                def set_instructor_availability_dict(start_time_index,end_time_index):
                    for time_index in range(start_time_index, end_time_index):
                        inst_avail_dict[day][time_index] = False


                if closest_teaching_range is not None:
                    
                    # checks if the next 30 min session goes over the duration 
                    if abs(requested_start_time_index + 1 - closest_teaching_range[0]) < duration_map[duration]:
                        set_instructor_availability_dict(requested_start_time_index + 1, closest_teaching_range[0])
                        
                    
                    if requested_end_time_index > closest_teaching_range[0]:
                        set_instructor_availability_dict(requested_start_time_index, closest_teaching_range[0])
                    
        return inst_avail_dict

    instructor_availability_map = set_instructor_availability_map(
        instructor_teaching_schedule_dict, instructor_availabilities_dict, duration
    )

    # convert datetime.timedelta to date.time - military time 
    for day in instructor_availability_map:
        for i, hour in enumerate(instructor_availability_map[day]):
            if hour == True:
                instructor_availability_map[day][i] = index_to_time(i, day, business_id)
    # remove False from list 
    for day in instructor_availability_map:
        instructor_availability_map[day] = list(
            filter(lambda a: a != False, instructor_availability_map[day])
        )
    
    return instructor_availability_map



from datetime import datetime, timedelta
import arrow
import calendar
import pytz

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import InstructorAvailability, InstructorOutOfOffice
from course.models import Course
from mainframe.permissions import ReadOnly, IsDev
from scheduler.models import Session
from scheduler.serializers import SessionSerializer


class SessionScheduleValidation(APIView):
    """
    Validates to see if session fits with instructor's availability
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request, instructor_id):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        date = request.query_params.get('date')
        datetime_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = calendar.day_name[datetime_obj.weekday()].lower()
        start_datetime = datetime.combine(
            datetime_obj.date(),
            datetime.strptime(start_time, '%H:%M').time()
        )
        end_datetime = datetime.combine(
            datetime_obj.date(),
            datetime.strptime(end_time, '%H:%M').time()
        )
        start_datetime = pytz.timezone(
            'America/Los_Angeles').localize(start_datetime).astimezone(pytz.utc)
        end_datetime = pytz.timezone(
            'America/Los_Angeles').localize(end_datetime).astimezone(pytz.utc)

        if not start_time or not end_time or not date:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'status': 'state_time, end_time, and date are all required parameters'}
            )

        # Check availabilities
        instructor_availabilities = InstructorAvailability.objects.filter(
            instructor=instructor_id,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time,
        )

        if not instructor_availabilities:
            return Response({
                'status': False,
                'reason': 'The instructor is not marked for being '
                          'available at this day of week and time.'
            })

        # Check conflicting sessions
        sessions = Session.objects.filter(
            Q(course__instructor=instructor_id),
            (Q(start_datetime__gte=start_datetime) & Q(start_datetime__lt=end_datetime)) |
            (Q(start_datetime__lte=start_datetime) & Q(end_datetime__gt=start_datetime)),
        )

        if sessions:
            return Response({
                'status': False,
                'conflicting_session': sessions[0].id,
                'reason': f'The instructor is teaching a session for the '
                          f'following course at the selected time: '
                          f'"{sessions[0].course.subject}"'
            })

        # Check out of office
        out_of_office = InstructorOutOfOffice.objects.filter(
            Q(instructor=instructor_id),
            (Q(start_datetime__gte=start_datetime) & Q(start_datetime__lt=end_datetime)) |
            (Q(start_datetime__lte=start_datetime) & Q(end_datetime__gt=start_datetime)),
        )

        if out_of_office:
            return Response({
                'status': False,
                'conflicting_out_of_office_start': out_of_office[0].start_datetime,
                'conflicting_out_of_office_end': out_of_office[0].end_datetime,
                'reason': f'The instructor is marked out of office at that time.'
            })

        return Response({'status': True})


class CourseScheduleValidation(APIView):
    """
    Validates to see if a course fits with instructor's availability
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request, instructor_id):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        start_datetime_obj = datetime.strptime(start_date, '%Y-%m-%d')
        day_of_week = calendar.day_name[start_datetime_obj.weekday()].lower()

        if not start_time or not end_time or not start_date or not end_date:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'status': 'state_time, end_time, start_date, and '
                                'end_date are all required parameters'}
            )

        # Check availabilities
        instructor_availabilities = InstructorAvailability.objects.filter(
            instructor=instructor_id,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time,
        )

        if not instructor_availabilities:
            return Response({
                'status': False,
                'reason': 'The instructor is not marked for being '
                          'available at this day of week and time.'
            })

        # Check conflicting courses
        courses = Course.objects.filter(
            Q(instructor=instructor_id),
            Q(day_of_week=day_of_week),
            (Q(start_date__gte=start_date) & Q(start_date__lt=end_date) |
             Q(start_date__lte=start_date) & Q(end_date__gt=start_date)),
            (Q(start_time__gte=start_time) & Q(start_time__lt=end_time) |
             Q(start_time__lte=start_time) & Q(end_time__gt=start_time)),
        )

        if courses:
            return Response({
                'status': False,
                'conflicting_course': courses[0].id,
                'reason': f'The instructor already is teaching the following '
                          f'course during those days and times: '
                          f'"{courses[0].subject}"'
            })

        return Response({'status': True})


class SessionViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def list(self, request):
        time_frame = request.query_params.get('time_frame', None)
        view_option = request.query_params.get('view_option', None)
        course_id = request.query_params.get('course_id', None)
        time_shift = int(request.query_params.get('time_shift', 0))
        queryset = self.get_queryset()

        if course_id is not None:
            queryset = queryset.filter(course = course_id)

        if view_option == 'class':
            queryset = queryset.filter(course__course_type=Course.CLASS)
        elif view_option == 'tutoring':
            queryset = queryset.filter(course__course_type=Course.TUTORING)

        now = datetime.now(tz=pytz.timezone('America/Los_Angeles'))
        base = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if time_frame == 'day':
            start_of_day = base + timedelta(days=time_shift)
            end_of_day = start_of_day + timedelta(days=1)
            queryset = queryset.filter(
                start_datetime__gte=start_of_day,
                end_datetime__lt=end_of_day
            )
        elif time_frame == 'week':
            start_of_week = base - timedelta(days=(base.weekday() + 1) % 7)
            start_of_week += timedelta(days=7 * time_shift)
            end_of_week = start_of_week + timedelta(days=7)
            queryset = queryset.filter(
                start_datetime__gte=start_of_week,
                end_datetime__lt=end_of_week
            )
        elif time_frame == 'month':
            start_of_month = base.replace(day=1)
            start_of_month = arrow.get(start_of_month).shift(months=time_shift).datetime
            if start_of_month.month == 12:
                end_of_month = start_of_month.replace(
                    year=start_of_month.year + 1,
                    month=1
                )
            else:
                end_of_month = start_of_month.replace(month=start_of_month.month + 1)
            queryset = queryset.filter(
                start_datetime__gte=start_of_month,
                end_datetime__lt=end_of_month
            )
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        course_id = request.query_params.get('course_id', None)
        if course_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        now = datetime.now()
        self.get_queryset().filter(
            course=course_id,
            end_datetime__gt=now
        ).delete()
        return Response(status.HTTP_204_NO_CONTENT)

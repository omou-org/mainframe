from datetime import datetime, timedelta
import pytz

from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from course.models import Course
from mainframe.permissions import ReadOnly, IsDev
from scheduler.models import Session
from scheduler.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def list(self, request):
        time_frame = request.query_params.get("time_frame", None)
        view_option = request.query_params.get("view_option", None)
        time_shift = int(request.query_params.get("time_shift", 0))
        queryset = self.get_queryset()
        if view_option == "class":
            queryset = queryset.filter(course__course_type=Course.CLASS)
        elif view_option == "tutoring":
            queryset = queryset.filter(course__course_type=Course.TUTORING)

        now = datetime.now(tz=pytz.timezone('US/Pacific'))
        base = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if time_frame == "day":
            start_of_day = base + timedelta(days=time_shift)
            end_of_day = start_of_day + timedelta(days=1)
            queryset = queryset.filter(
                start_datetime__gte=start_of_day,
                end_datetime__lt=end_of_day
            )
        elif time_frame == "week":
            start_of_week = base - timedelta(days=(base.weekday() + 1) % 7)
            start_of_week += timedelta(days=7 * time_shift)
            end_of_week = start_of_week + timedelta(days=7)
            queryset = queryset.filter(
                start_datetime__gte=start_of_week,
                end_datetime__lt=end_of_week
            )
        elif time_frame == "month":
            start_of_month = base.replace(day=1)
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
        course_id = request.query_params.get("course_id", None)
        if course_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        now = datetime.now()
        self.get_queryset().filter(
            course=course_id,
            end_datetime__gt=now
        ).delete()
        return Response(status.HTTP_204_NO_CONTENT)

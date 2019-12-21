from datetime import datetime, timedelta

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from scheduler.serializers import (
    SessionSerializer
)

from course.models import Course
from scheduler.models import Session
from scheduler.serializers import


class SessionViewSet(viewsets.ModelViewSet):
   queryset = Session.objects.all()
   serializer_class = SessionSerializer

    def list(self, request):
        time_frame = request.query_params.get("time_frame", None)
        view_option = request.query_params.get("view_option", None)
        queryset = self.get_queryset()
        if view_option == "class":
            queryset = queryset.filter(course__type=Course.CLASS)
        elif view_option == "tutoring":
            queryset = queryset.filter(course__type=Course.TUTORING)

        now = datetime.now()
        if time_frame == "day":
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(
                start_datetime__gte=start_of_day)
        elif time_frame == "week":
            pass
        elif time_frame == "month":
            pass
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

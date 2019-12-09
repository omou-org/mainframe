
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from scheduler.serializers import (
    SessionSerializer
)

from course.models import Course
from mainframe.permissions import IsDev, ReadOnly
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
        if view_option == "tutoring":
            queryset = queryset.filter(course__type=Course.TUTORING)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

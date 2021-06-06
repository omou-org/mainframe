from scheduler.models import Session
from rest_framework import serializers


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session

        fields = (
            "id",
            "course",
            "instructor",
            "details",
            "start_datetime",
            "end_datetime",
            "is_confirmed",
            "title",
        )

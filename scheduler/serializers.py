from django.db import transaction

from scheduler.models import Session
from rest_framework import serializers


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session

        fields = (
            'id',
            'student',
            'course',
            'payment',
        )

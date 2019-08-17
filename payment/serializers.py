from rest_framework import serializers

from payment.models import (
    Payment,
    SessionPayment
)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment

        read_only_fields = (
            'id',
            'date_time'
        )
        fields = (
            'id',
            'method',
            'amount',
            'description',
            'date_time',
            'student',
            'course'
        )


class SessionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPayment

        read_only_fields = (
            'id',
            'date_time'
        )
        fields = (
            'id',
            'status',
            'amount',
            'date_time',
            'student',
            'session'
        )

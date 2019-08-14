from payment.models import Payment
from rest_framework import serializers


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

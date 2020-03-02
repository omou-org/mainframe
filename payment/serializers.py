from django.db import transaction
from rest_framework import serializers

from account.models import Parent
from course.models import Course, Enrollment
from payment.models import Payment, Registration


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        ref_name = 'enrollment_for_registration'

        fields = (
            'student',
            'course',
        )


class RegistrationSerializer(serializers.ModelSerializer):
    enrollment_details = EnrollmentSerializer(read_only=True, source='enrollment')

    class Meta:
        model = Registration

        read_only_fields = (
            'id',
            'payment',
            'updated_at',
            'created_at',
        )

        fields = (
            'id',
            'attendance_start_date',
            'payment',
            'enrollment',
            'num_sessions',
            'enrollment_details',
            'updated_at',
            'created_at',
        )


class PaymentSerializer(serializers.ModelSerializer):
    registrations = RegistrationSerializer(many=True, source='registration_set')

    @transaction.atomic
    def create(self, validated_data):
        registrations = validated_data.pop("registration_set")
        payment = Payment.objects.create(
            **validated_data,
        )

        # deduct account_balance from parent balance
        if validated_data["account_balance"] > 0.0:
            parent = Parent.objects.get(user_id = validated_data["parent"])
            parent.balance -= validated_data["account_balance"]
            parent.save()

        # create registrations
        for registration in registrations:
            Registration.objects.create(
                payment=payment,
                enrollment=registration["enrollment"],
                num_sessions=registration["num_sessions"]
            )
        return payment

    class Meta:
        model = Payment

        fields = (
            'id',
            'parent',
            'sub_total',
            'price_adjustment',
            'total',
            'account_balance',
            'discount_total',
            'method',
            'registrations',
            'updated_at',
            'created_at'
        )

        read_only_fields = (
            'id',
            'updated_at',
            'created_at'
        )
